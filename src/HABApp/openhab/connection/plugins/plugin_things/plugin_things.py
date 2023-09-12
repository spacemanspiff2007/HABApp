from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import msgspec

import HABApp
import HABApp.openhab.events
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.files.file import HABAppFile
from HABApp.core.files.folders import add_folder as add_habapp_folder
from HABApp.core.files.watcher import AggregatingAsyncEventHandler
from HABApp.core.lib import PendingFuture
from HABApp.core.logger import log_warning, HABAppError
from HABApp.openhab.connection.connection import OpenhabConnection
from HABApp.openhab.connection.plugins.plugin_things.cfg_validator import validate_cfg, InvalidItemNameError
from HABApp.openhab.connection.plugins.plugin_things.filters import THING_ALIAS, CHANNEL_ALIAS
from HABApp.openhab.connection.plugins.plugin_things.filters import apply_filters, log_overview
from ._log import log
from .file_writer import ItemsFileWriter
from .item_worker import create_item, cleanup_items
from .thing_worker import update_thing_cfg


class DuplicateItemError(Exception):
    pass


class TextualThingConfigPlugin(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self):
        super().__init__()
        self.created_items: dict[str, set[str]] = {}
        self.do_cleanup = PendingFuture(self.clean_items, 120)

        self.watcher: AggregatingAsyncEventHandler | None = None

        self.cache_ts: float = 0.0
        self.cache_cfg: list[dict[str, Any]] = []

    async def on_setup(self):
        path = HABApp.CONFIG.directories.config
        if path is None:
            return None

        if self.watcher is not None:
            return None

        class HABAppThingConfigFile(HABAppFile):
            LOGGER = log
            LOAD_FUNC = self.file_load
            UNLOAD_FUNC = self.file_unload

        folder = add_habapp_folder('config/', path, 50)
        folder.add_file_type(HABAppThingConfigFile)
        self.watcher = folder.add_watch('.yml')

    async def file_unload(self, prefix: str, path: Path):
        return None

    async def on_connected(self):
        if self.watcher is None:
            return None

        await self.load_thing_data(always=True)
        await self.watcher.trigger_all()

    @HABApp.core.wrapper.ignore_exception
    async def clean_items(self):
        items = set()
        for s in self.created_items.values():
            items.update(s)
        await cleanup_items(items)

    async def load_thing_data(self, always: bool) -> list[dict[str, Any]]:
        if always or not self.cache_cfg or time.time() - self.cache_ts > 20:
            self.cache_cfg = [msgspec.to_builtins(k) for k in await HABApp.openhab.interface_async.async_get_things()]
            self.cache_ts = time.time()
        return self.cache_cfg

    async def file_load(self, name: str, path: Path):
        # we have to check the naming structure because we get file events for the whole folder
        _name = path.name.lower()
        if not _name.startswith('thing_') or not _name.endswith('.yml'):
            log.warning(f'Name for "{name}" does not start with "thing_" -> skip!')
            return None

        # only load if we don't supply the data
        data = await self.load_thing_data(always=False)

        # remove created items
        self.created_items.pop(path.name, None)
        created_items = self.created_items.setdefault(path.name, set())

        # shedule cleanup
        self.do_cleanup.reset()

        # output file
        items_file_path = path.with_suffix('.items')
        items_file_writer = ItemsFileWriter()

        # we also get events when the file gets deleted
        if not path.is_file():
            log.debug(f'File {path} does not exist -> skipping Thing configuration!')
            return None
        log.debug(f'Loading {name}!')

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
                            raise DuplicateItemError(f'Duplicate item: {name}')
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
                                    raise DuplicateItemError(f'Duplicate item: {name}')
                                create_items[name] = item_cfg

                    # newline only if we create logs
                    if test and (cfg_entry.create_items or cfg_entry.channels):
                        log.info('')
            except InvalidItemNameError as e:
                HABAppError(log).add_exception(e).dump()
                continue
            except DuplicateItemError as e:
                # Duplicates should never happen, the user clearly made a mistake, that's why we exit here
                HABAppError(log).add_exception(e).dump()
                return None

            # Create all items
            for item_cfg in create_items.values():
                created = await create_item(item_cfg, test)
                if created:
                    created_items.add(item_cfg.name)

            self.do_cleanup.reset()

            items_file_writer.add_items(create_items.values())
            self.cache_cfg = []

        items_file_writer.create_file(items_file_path)
