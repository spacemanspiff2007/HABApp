from __future__ import annotations

import asyncio
from time import monotonic

import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.openhab.connection.connection import OpenhabConnection, OpenhabContext
from HABApp.openhab.connection.handler.func_async import async_get_system_info


async def _start_level_reached() -> tuple[bool, None | int]:
    start_level_min = HABApp.CONFIG.openhab.general.min_start_level

    if (system_info := await async_get_system_info()) is None:
        return False, None

    start_level_is = system_info.start_level

    return start_level_is >= start_level_min, start_level_is


class WaitForStartlevelPlugin(BaseConnectionPlugin[OpenhabConnection]):

    async def on_connected(self, context: OpenhabContext, connection: OpenhabConnection):
        level_reached, level = await _start_level_reached()

        if level_reached:
            context.waited_for_openhab = False
            return None

        context.waited_for_openhab = False
        log = connection.log

        log.info('Waiting for openHAB startup to be complete')

        last_level: int = -100

        timeout_duration = 10 * 60
        timeout_start_at_level = 70
        timeout_timestamp = 0

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
                    timeout_timestamp = monotonic()
                    log.debug('Starting start level timeout')

            # timeout is running
            if timeout_timestamp and monotonic() - timeout_timestamp > timeout_duration:
                log.warning(f'Starting even though openHAB is not ready yet (start level: {level})')
                break

            # update last level!
            last_level = level

        log.info('openHAB startup complete')
