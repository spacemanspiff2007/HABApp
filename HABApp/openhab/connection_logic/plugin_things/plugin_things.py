import asyncio
from pathlib import Path
from typing import Dict, Set, List

import HABApp
from HABApp.core.lib import PendingFuture
from HABApp.core.logger import log_warning, HABAppError
from HABApp.openhab.connection_handler.func_async import async_get_things
from HABApp.openhab.connection_logic.plugin_things.cfg_validator import validate_cfg, InvalidItemNameError
from HABApp.openhab.connection_logic.plugin_things.filters import THING_ALIAS, CHANNEL_ALIAS
from HABApp.openhab.connection_logic.plugin_things.filters import apply_filters, log_overview
from ._log import log
from .item_worker import create_item, cleanup_items
from .items_file import create_items_file
from .thing_worker import update_thing_cfg
from .._plugin import OnConnectPlugin


class ManualThingConfig(OnConnectPlugin):

    def __init__(self):
        super().__init__()
        self.created_items: Dict[str, Set[str]] = {}
        self.do_cleanup = PendingFuture(self.clean_items, 120)

    def setup(self):
        if not HABApp.CONFIG.directories.config.is_dir():
            log.info('Config folder does not exist - textual thing config disabled!')
            return None

        # Add event bus listener
        HABApp.core.EventBus.add_listener(
            HABApp.core.EventBusListener(
                HABApp.core.const.topics.FILES,
                HABApp.core.WrappedFunction(self.file_load_event),
                HABApp.core.events.habapp_events.RequestFileLoadEvent
            )
        )

        # watch folder
        HABApp.core.files.watch_folder(HABApp.CONFIG.directories.config, '.yml', True)

    async def file_load_event(self, event: HABApp.core.events.habapp_events.RequestFileLoadEvent):
        if HABApp.core.files.file_name.is_config(event.name):
            await self.update_thing_config(event.get_path())

    async def on_connect_function(self):
        try:
            await asyncio.sleep(0.3)

            files = list(HABApp.core.lib.list_files(HABApp.CONFIG.directories.config, '.yml'))
            if not files:
                log.debug(f'No manual configuration files found in {HABApp.CONFIG.directories.config}')
                return None

            # if oh is not ready we will get None, but we will trigger again on reconnect
            data = await async_get_things()
            if data is None:
                return None

            for f in files:
                await self.update_thing_config(f, data)
        except asyncio.CancelledError:
            pass

    @HABApp.core.wrapper.ignore_exception
    async def clean_items(self):
        items = set()
        for s in self.created_items.values():
            items.update(s)
        await cleanup_items(items)

    async def update_thing_configs(self, files: List[Path]):
        data = await async_get_things()
        if data is None:
            return None

        for file in files:
            await self.update_thing_config(file, data)

    @HABApp.core.wrapper.ignore_exception
    async def update_thing_config(self, path: Path, data=None):
        # we have to check the naming structure because we get file events for the whole folder
        _name = path.name.lower()
        if not _name.startswith('thing_') or not _name.endswith('.yml'):
            return None

        # only load if we don't supply the data
        if data is None:
            data = await async_get_things()

        # remove created items
        self.created_items.pop(path.name, None)
        created_items = self.created_items.setdefault(path.name, set())

        # shedule cleanup
        self.do_cleanup.reset()

        # output file
        output_file = path.with_suffix('.items')
        if output_file.is_file():
            output_file.unlink()

        # we also get events when the file gets deleted
        if not path.is_file():
            log.debug(f'File {path} does not exist -> skipping Thing configuration!')
            return None
        log.debug(f'Loading {path}!')

        # load the config file
        with path.open(mode='r', encoding='utf-8') as file:
            try:
                cfg = HABApp.core.const.yml.load(file)
            except Exception as e:
                HABAppError(log).add_exception(e).dump()
                return None

        # validate configuration
        cfg = validate_cfg(cfg, path.name)
        if cfg is None:
            return None

        # if one entry has test set we show an overview of all the things
        if any(map(lambda x: x.test, cfg)):
            log_overview(data, THING_ALIAS, 'Thing overview')

        # process each thing part in the cfg
        for cfg_entry in cfg:
            test: bool = cfg_entry.test
            things = list(apply_filters(cfg_entry.filter, data, test))

            # show a warning we found no Things
            if not things:
                log_warning(log, f'No things matched for {cfg_entry.filter}')
                continue

            # update thing configuration
            if cfg_entry.thing_config:
                await update_thing_cfg(cfg_entry.thing_config, things, test)

            try:
                # item creation for every thing
                create_items = {}
                shown_types = set()
                for thing in things:
                    thing_context = {k: thing.get(alias, '') for k, alias in THING_ALIAS.items()}

                    # create items without channel
                    for item_cfg in cfg_entry.get_items(thing_context):
                        name = item_cfg.name
                        if name in create_items:
                            raise ValueError(f'Duplicate item: {name}')
                        create_items[name] = item_cfg

                    # Channel overview, only if we have something configured
                    if test and cfg_entry.channels:
                        __thing_type = thing_context['thing_type']
                        if __thing_type not in shown_types:
                            shown_types.add(__thing_type)
                            log_overview(thing['channels'], CHANNEL_ALIAS, heading=f'Channels for {__thing_type}')

                    # do channel things
                    for channel_cfg in cfg_entry.channels:
                        channels = apply_filters(channel_cfg.filter, thing['channels'], test)
                        for channel in channels:
                            channel_context = {k: channel.get(alias, '') for k, alias in CHANNEL_ALIAS.items()}
                            channel_context.update(thing_context)

                            for item_cfg in channel_cfg.get_items(channel_context):
                                item_cfg.link = channel['uid']
                                name = item_cfg.name

                                if name in create_items:
                                    raise ValueError(f'Duplicate item: {name}')
                                create_items[name] = item_cfg

                    # newline only if we create logs
                    if test and (cfg_entry.create_items or cfg_entry.channels):
                        log.info('')
            except InvalidItemNameError as e:
                HABAppError(log).add_exception(e).dump()
                continue

            # Create all items
            for item_cfg in create_items.values():
                created = await create_item(item_cfg, test)
                if created:
                    created_items.add(item_cfg.name)

            self.do_cleanup.reset()

            create_items_file(output_file, create_items)


PLUGIN_MANUAL_THING_CFG = ManualThingConfig.create_plugin()
