import faulthandler
import logging
import signal
from asyncio import sleep
from datetime import datetime
from typing import Final, TextIO

import HABApp
from HABApp.config.logging import rotate_file
from HABApp.core.asyncio import create_task
from HABApp.core.wrapper import log_exception


TRACEBACK_FILE: TextIO | None = None


def setup_debug() -> None:
    global TRACEBACK_FILE

    debug = HABApp.CONFIG.habapp.debug
    periodic_tb_cfg = debug.periodic_traceback
    event_loop_cfg = debug.watch_event_loop
    tb_on_shutdown_signal = debug.traceback_on_shutdown_signal

    if not event_loop_cfg.enabled and not tb_on_shutdown_signal and not periodic_tb_cfg.enabled:
        return None

    file: Final = HABApp.CONFIG.directories.logging / 'HABApp_traceback.log'
    logging.getLogger('HABApp').info(f'Dumping traceback to {file}')

    rotate_file(file, 3)

    TRACEBACK_FILE = file.open('a')
    HABApp.core.shutdown.register(TRACEBACK_FILE.close, last=True, msg='Closing traceback file')

    if periodic_tb_cfg.enabled:
        task = create_task(
            dump_traceback_task(
                int(periodic_tb_cfg.delay.total_seconds()),
                int(periodic_tb_cfg.interval.total_seconds())
            ),
            name='DumpTracebackTask'
        )
        HABApp.core.shutdown.register(task.cancel, msg='Stopping traceback task')

    if tb_on_shutdown_signal:
        TRACEBACK_FILE.write('Dumping on shutdown signal\n')
        TRACEBACK_FILE.flush()

        faulthandler.register(signal.SIGINT, TRACEBACK_FILE, all_threads=True)
        faulthandler.register(signal.SIGTERM, TRACEBACK_FILE, all_threads=True)

    if event_loop_cfg.enabled:
        task = create_task(
            watch_event_loop_task(
                sleep_secs=int(event_loop_cfg.reset_every.total_seconds()),
                timeout_secs=int(event_loop_cfg.timeout.total_seconds()),
            ),
            name='WatchEventLoopTask'
        )
        HABApp.core.shutdown.register(task.cancel, msg='Stopping WatchEventLoopTask')


@log_exception
async def dump_traceback_task(delay: int, interval: int) -> None:

    await sleep(0.2)
    TRACEBACK_FILE.write('Dumping traceback\n')
    TRACEBACK_FILE.write(f'Start: {datetime.now()}\n')
    TRACEBACK_FILE.write(f'Delay: {delay:d}s Interval: {interval:d}s\n')
    TRACEBACK_FILE.write(f'\n{"-" * 80}\n')
    TRACEBACK_FILE.flush()

    await sleep(delay)

    while True:
        TRACEBACK_FILE.write(f'{datetime.now()}\n\n')
        faulthandler.dump_traceback(TRACEBACK_FILE, all_threads=True)
        TRACEBACK_FILE.write(f'\n{"-" * 80}\n')

        await sleep(interval)


@log_exception
async def watch_event_loop_task(sleep_secs: int, timeout_secs: int) -> None:

    TRACEBACK_FILE.write(f'Watching event loop\nReset: {sleep_secs:d}s Timeout: {timeout_secs:d}s\n\n')
    TRACEBACK_FILE.flush()

    while True:
        faulthandler.dump_traceback_later(timeout_secs, file=TRACEBACK_FILE, exit=True)
        await sleep(sleep_secs)
