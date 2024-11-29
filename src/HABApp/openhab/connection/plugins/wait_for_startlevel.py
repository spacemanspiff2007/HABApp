from __future__ import annotations

import asyncio
import logging

import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.config.models.openhab import General as OpenHABGeneralConfig
from HABApp.core import shutdown
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.lib import Timeout, ValueChange
from HABApp.openhab.connection.connection import OpenhabConnection, OpenhabContext
from HABApp.openhab.connection.handler.func_async import async_get_system_info


class WaitForStartlevelPlugin(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)

    async def on_connected(self, context: OpenhabContext, connection: OpenhabConnection):
        if not context.is_oh41:
            return await self.__on_connected_old(context, connection)

        return await self.__on_connected_new(context, connection)

    async def __on_connected_new(self, context: OpenhabContext, connection: OpenhabConnection):
        oh_general = HABApp.CONFIG.openhab.general

        if (system_info := await async_get_system_info()) is not None:  # noqa: SIM102
            # If openHAB is already running we have a fast exit path here
            if system_info.uptime >= oh_general.min_uptime and system_info.start_level >= oh_general.min_start_level:
                context.waited_for_openhab = False

                # Show a hint in case it's possible to increase the start level
                # A higher start level means a more consistent startup and thus is more desirable
                if system_info.start_level > oh_general.min_start_level:
                    _field_name_cfg = 'min_start_level'
                    if (alias := OpenHABGeneralConfig.model_fields[_field_name_cfg].alias) is not None:
                        _field_name_cfg = alias

                    logging.getLogger('HABApp').info(
                        f'Openhab reached start level {system_info.start_level:d} but HABApp only waits until '
                        f'level {oh_general.min_start_level:d} is reached. '
                        f'Consider increasing "{_field_name_cfg:s}" in the HABApp configuration. '
                    )

                return None

        log = connection.log
        log.info('Waiting for openHAB startup to be complete')
        context.waited_for_openhab = True

        timeout_start_at_level = 70
        timeout = Timeout(10 * 60, start=False)

        level_change: ValueChange[int] = ValueChange()

        sleep_secs = 1

        while not shutdown.is_requested():
            await asyncio.sleep(sleep_secs)
            sleep_secs = 1

            if (system_info := await async_get_system_info()) is None:
                if level_change.set_missing().changed:
                    log.debug('Start level: not received!')
                continue

            level = system_info.start_level

            # Wait for min uptime
            if system_info.uptime < (min_uptime := oh_general.min_uptime):
                sleep_secs = min_uptime - system_info.uptime
                log.debug(f'Waiting {sleep_secs:d} secs until openHAB uptime of {min_uptime:d} secs is reached')
                continue

            # timeout is running
            if timeout.is_running_and_expired():
                log.warning(f'Starting even though openHAB is not ready yet (start level: {level})')
                break

            # log only when level changed, so we don't spam the log
            if level_change.set_value(level).changed:

                log.debug(f'Start level: {level:d}')
                if level >= oh_general.min_start_level:
                    break

                # Wait but start eventually because sometimes we have a bad configured thing or an offline gateway
                # that prevents the start level from advancing
                # This is a safety net, so we properly start e.g. after a power outage
                # When starting manually one should fix the blocking thing
                if level >= timeout_start_at_level:
                    timeout.start()
                    log.debug('Starting start level timeout')

        if shutdown.is_requested():
            return None
        log.info('openHAB startup complete')

    async def __on_connected_old(self, context: OpenhabContext, connection: OpenhabConnection):

        level_reached, level = await _start_level_reached()

        if level_reached:
            context.waited_for_openhab = False
            return None

        context.waited_for_openhab = False
        log = connection.log

        log.info('Waiting for openHAB startup to be complete')

        last_level: int = -100

        timeout_start_at_level = 70
        timeout = Timeout(10 * 60, start=False)

        while not level_reached:
            await asyncio.sleep(1)

            level_reached, level = await _start_level_reached()

            # show start level change
            if last_level != level:
                if level is None:
                    log.debug('Start level: not received!')
                    level = -10
                else:
                    log.debug(f'Start level: {level}')

                # Wait but start eventually because sometimes we have a bad configured thing or an offline gateway
                # that prevents the start level from advancing
                # This is a safety net, so we properly start e.g. after a power outage
                # When starting manually one should fix the blocking thing
                if level >= timeout_start_at_level:
                    timeout.start()
                    log.debug('Starting start level timeout')

            # timeout is running
            if timeout.is_running_and_expired():
                log.warning(f'Starting even though openHAB is not ready yet (start level: {level})')
                break

            # update last level!
            last_level = level

        log.info('openHAB startup complete')


async def _start_level_reached() -> tuple[bool, None | int]:
    start_level_min = HABApp.CONFIG.openhab.general.min_start_level

    if (system_info := await async_get_system_info()) is None:
        return False, None

    start_level_is = system_info.start_level

    return start_level_is >= start_level_min, start_level_is
