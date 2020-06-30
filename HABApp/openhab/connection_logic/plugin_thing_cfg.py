import asyncio
import logging
from pathlib import Path
from typing import Optional

import HABApp
from HABApp.openhab.definitions.exceptions import ThingNotFoundError
from HABApp.openhab.definitions.helpers.thing_config import ThingConfigChanger
from ._plugin import PluginBase
from ..interface_async import async_get_thing, async_set_thing_cfg

log = logging.getLogger('HABApp.openhab.config')


class SyncThingConfig(PluginBase):
    def __init__(self):
        self.fut: Optional[asyncio.Future] = None

    def setup(self):
        pass

    def on_connect(self):
        async def wait_and_update():
            try:
                await asyncio.sleep(2)
                for f in HABApp.core.lib.list_files(HABApp.CONFIG.directories.config, '.yml'):
                    await self.update_thing_config(f)
            except asyncio.CancelledError:
                pass
        self.fut = asyncio.ensure_future(wait_and_update(), loop=HABApp.core.const.loop)

    def on_disconnect(self):
        if self.fut is not None:
            self.fut.cancel()
            self.fut = None

    @HABApp.core.wrapper.log_exception
    async def update_thing_config(self, path: Path):
        # we have to check the naming structure because we get file events for the whole folder
        _name = path.name.lower()
        if not _name.startswith('thingconfig') or not _name.endswith('.yml'):
            return None

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
                thing = await async_get_thing(uid)
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

            if not cfg.new:
                continue

            try:
                ret = await async_set_thing_cfg(uid, cfg=cfg.new)
                if ret is None:
                    continue
            except Exception as e:
                log.error(f'Could not set new config: {e}!')
                continue
            log.info('Config successfully updated!')


PLUGIN_THING_CFG = SyncThingConfig.create_plugin()
