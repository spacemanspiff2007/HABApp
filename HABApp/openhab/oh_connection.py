import asyncio
import logging
import re
import time
import typing
from pathlib import Path

from bidict import bidict

import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.core.wrapper import ignore_exception, log_exception
from HABApp.openhab.map_events import get_event
from .definitions.rest import ThingNotFoundError
from .http_connection import HttpConnection, HttpConnectionEventHandler
from .oh_interface import get_openhab_interface
from ..config import Openhab as OpenhabConfig

log = logging.getLogger('HABApp.openhab.Connection')


class OpenhabConnection(HttpConnectionEventHandler):

    def __init__(self, config: OpenhabConfig, shutdown):
        assert isinstance(config, OpenhabConfig), type(config)
        assert isinstance(shutdown, HABApp.runtime.ShutdownHelper), type(shutdown)

        self.config = config

        self.connection = HttpConnection(self, self.config)
        self.interface = get_openhab_interface(self.connection)

        self.__ping_sent = 0
        self.__ping_received = 0

        # Add the ping listener, this works because connect is the last step
        if self.config.ping.enabled:
            listener = HABApp.core.EventBusListener(
                self.config.ping.item,
                HABApp.core.WrappedFunction(self.ping_received),
                HABApp.openhab.events.ItemStateEvent
            )
            HABApp.core.EventBus.add_listener(listener)

        shutdown.register_func(self.shutdown)

        # todo: currently this does not work
        # # reload config
        # HABApp.CONFIG.openhab.connection.subscribe_for_changes(
        #     lambda : asyncio.run_coroutine_threadsafe(self.__create_session(), self.runtime.loop).result()
        # )

        self.__async_sse: asyncio.Future = None
        self.__async_items: asyncio.Future = None
        self.__async_ping: asyncio.Future = None

    def on_connected(self):
        # Start SSE Processing
        self.__async_sse = asyncio.ensure_future(self.connection.async_process_sse_events())

        # Read all Items
        self.__async_items = asyncio.ensure_future(self.update_all_items())

        # start ping
        self.__async_ping = asyncio.ensure_future(self.async_ping())

        # todo: move this somewhere proper
        async def wait_and_update():
            await asyncio.sleep(2)
            for f in HABApp.core.lib.list_files(HABApp.CONFIG.directories.config, '.yml'):
                await self.update_thing_config(f)
        asyncio.ensure_future(wait_and_update())

    @log_exception
    def on_disconnected(self):

        for future in (self.__async_sse, self.__async_items, self.__async_ping):
            if future is None:
                continue
            # if it is still running cancel
            if not future.done():
                future.cancel()

    async def start(self):
        await self.connection.try_connect()

    @log_exception
    def shutdown(self):
        self.on_disconnected()
        self.connection.cancel_connect()

    def ping_received(self, event):
        self.__ping_received = time.time()

    @log_exception
    async def async_ping(self):

        if not self.config.ping.enabled:
            return None

        log.debug('Started ping')
        while self.config.ping.enabled:
            self.interface.post_update(
                self.config.ping.item,
                f'{(self.__ping_received - self.__ping_sent) * 1000:.1f}' if self.__ping_received else '0'
            )

            self.__ping_sent = time.time()
            await asyncio.sleep(self.config.ping.interval)

    @ignore_exception
    def on_sse_event(self, event_dict: dict):

        # Lookup corresponding OpenHAB event
        event = get_event(event_dict)

        # Update item in registry BEFORE posting to the event bus
        # so the items have the correct state when we process the event in a rule
        try:
            if isinstance(event, HABApp.core.events.ValueUpdateEvent):
                __item = HABApp.core.Items.get_item(event.name)  # type: HABApp.core.items.base_item.BaseValueItem
                __item.set_value(event.value)
                HABApp.core.EventBus.post_event(event.name, event)
                return None
            elif isinstance(event, HABApp.openhab.events.ThingStatusInfoEvent):
                __thing = HABApp.core.Items.get_item(event.name)   # type: HABApp.openhab.items.Thing
                __thing.process_event(event)
                HABApp.core.EventBus.post_event(event.name, event)
                return None
        except HABApp.core.Items.ItemNotFoundException:
            pass

        # Events which change the ItemRegistry
        if isinstance(event, (HABApp.openhab.events.ItemAddedEvent, HABApp.openhab.events.ItemUpdatedEvent)):
            item = HABApp.openhab.map_items(event.name, event.type, 'NULL')
            if item is None:
                return None

            # check already existing item so we can print a warning if something changes
            try:
                existing_item = HABApp.core.Items.get_item(item.name)
                if isinstance(existing_item, item.__class__):
                    # it's the same item class so we don't replace it!
                    item = existing_item
                else:
                    log.warning(f'Item changed type from {existing_item.__class__} to {item.__class__}')
            except HABApp.core.Items.ItemNotFoundException:
                pass

            # always overwrite with new definition
            HABApp.core.Items.set_item(item)

        elif isinstance(event, HABApp.openhab.events.ItemRemovedEvent):
            HABApp.core.Items.pop_item(event.name)

        # Send Event to Event Bus
        HABApp.core.EventBus.post_event(event.name, event)
        return None

    @ignore_exception
    async def update_all_items(self):
        data = await self.connection.async_get_items()
        if data is None:
            return None

        found_items = len(data)
        for _dict in data:
            item_name = _dict['name']
            new_item = HABApp.openhab.map_items(item_name, _dict['type'], _dict['state'])
            if new_item is None:
                continue

            try:
                # if the item already exists and it has the correct type just update its state
                # Since we load the items before we load the rules this should actually never happen
                existing_item = HABApp.core.Items.get_item(item_name)   # type: HABApp.core.items.BaseValueItem
                if isinstance(existing_item, new_item.__class__):
                    existing_item.set_value(new_item.value)  # use the converted state from the new item here
                    new_item = existing_item
            except HABApp.core.Items.ItemNotFoundException:
                pass

            # create new item or change item type
            HABApp.core.Items.set_item(new_item)

        # remove items which are no longer available
        ist = set(HABApp.core.Items.get_all_item_names())
        soll = {k['name'] for k in data}
        for k in ist - soll:
            if isinstance(HABApp.core.Items.get_item(k), HABApp.openhab.items.OpenhabItem):
                HABApp.core.Items.pop_item(k)

        log.info(f'Updated {found_items:d} Items')


        # try to update things, too
        data = await self.connection.async_get_things()
        if data is None:
            return None

        Thing = HABApp.openhab.items.Thing
        for t_dict in data:
            name = t_dict['UID']
            try:
                thing = HABApp.core.Items.get_item(name)
                if not isinstance(thing, Thing):
                    log.warning(f'Item {name} has the wrong type ({type(thing)}), expected Thing')
                    thing = Thing(name)
            except HABApp.core.Items.ItemNotFoundException:
                thing = Thing(name)

            thing.status = t_dict['statusInfo']['status']
            HABApp.core.Items.set_item(thing)

        # remove things which were deleted
        ist = set(HABApp.core.Items.get_all_item_names())
        soll = {k['UID'] for k in data}
        for k in ist - soll:
            if isinstance(HABApp.core.Items.get_item(k), Thing):
                HABApp.core.Items.pop_item(k)

        log.info(f'Updated {len(data):d} Things')

        return None

    @HABApp.core.wrapper.log_exception
    async def update_thing_config(self, path: Path):
        # we have to check the naming structure because we get file events for the whole folder
        _name = path.name.lower()
        if not _name.startswith('thingconfig') or not _name.endswith('.yml'):
            return None

        log = logging.getLogger('HABApp.openhab.Config')
        # we also get events when the file gets deleted
        if not path.is_file():
            log.debug(f'File {path} does not exist -> skipping Thing configuration!')
            return None

        yml = HABApp.parameters.parameter_files._yml_setup
        with path.open(mode='r', encoding='utf-8') as file:
            manu_cfg = yml.load(file)

        if not manu_cfg or not isinstance(manu_cfg, dict):
            log.warning(f'File {path} is empty!')
            return None

        for uid, target_cfg in manu_cfg.items():
            try:
                thing = await self.connection.async_get_thing(uid)
            except ThingNotFoundError:
                log.error(f'Thing with uid "{uid}" does not exist!')
                continue

            if thing.configuration is None:
                log.error('Thing can not be configured!')
                continue

            cfg = ThingConfigChanger.from_dict(thing.configuration)

            log.info(f'Checking {uid}: {thing.label}')
            keys_ok = True
            for k in target_cfg:
                if k in cfg:
                    continue
                keys_ok = False
                log.error(f' - Config value "{k}" does not exist!')

            if not keys_ok:
                # show list with available entries
                log.error('   Available:')
                for k, v in sorted(filter(lambda x: isinstance(x[0], str), cfg.items())):
                    if k.startswith('action_') or k in ('node_id', 'wakeup_node'):
                        continue
                    log.error(f'    - {k}: {v}')
                for k, v in sorted(filter(lambda x: isinstance(x[0], int), cfg.items())):
                    log.error(f'    - {k:3d}: {v}')

                # don't process entries with invalid keys
                continue

            # Check the current value
            for k, target_val in target_cfg.items():
                current_val = cfg[k]
                if current_val == target_val:
                    log.info(f' - {k} is already {target_val}')
                    continue

                log.info(f' - Set {k} to {target_val}')
                cfg[k] = target_val

            if not cfg.new or self.connection.is_read_only:
                continue

            try:
                await self.connection.async_set_thing_cfg(uid, cfg=cfg.new)
            except Exception as e:
                log.error(f'Could not set new config: {e}!')
                continue
            log.info('Config successfully updated!')


class ThingConfigChanger:
    zw_param = re.compile(r'config_(?P<p>\d+)_(?P<w>\d+)')
    zw_group = re.compile(r'group_(\d+)')

    @classmethod
    def from_dict(cls, _in: dict) -> 'ThingConfigChanger':
        c = cls()
        c.org = _in
        for k in _in:
            # Z-Wave Params -> 0
            m = ThingConfigChanger.zw_param.fullmatch(k)
            if m:
                c.alias[int(m.group(1))] = k
                continue

            # Z-Wave Groups to Group1
            m = ThingConfigChanger.zw_group.fullmatch(k)
            if m:
                c.alias[f'Group{m.group(1)}'] = k
                continue
        return c

    def __init__(self):
        self.alias = bidict()
        self.org: typing.Dict[str, typing.Any] = {}
        self.new: typing.Dict[str, typing.Any] = {}

    def __getitem__(self, key):
        return self.org[self.alias.get(key, key)]

    def __setitem__(self, key, item):
        self.new[self.alias.get(key, key)] = item

    def __contains__(self, key):
        return self.alias.get(key, key) in self.org

    def keys(self):
        return (self.alias.inverse.get(k, k) for k in self.org.keys())

    def values(self):
        return self.org.values()

    def items(self):
        for k, v in zip(self.keys(), self.values()):
            yield k, v
