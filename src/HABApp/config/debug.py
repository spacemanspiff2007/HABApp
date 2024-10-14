import logging
from asyncio import sleep
from faulthandler import dump_traceback
from pathlib import Path

import HABApp
from HABApp.core.asyncio import create_task
from HABApp.core.items.base_valueitem import datetime


def _get_file_path(nr: int) -> Path:
    assert nr >= 0  # noqa: S101
    log_dir = HABApp.CONFIG.directories.logging
    ctr = f'.{nr}' if nr else ''
    return log_dir / f'HABApp_traceback{ctr:s}.log'


def setup_debug() -> None:
    debug = HABApp.CONFIG.habapp.debug
    if (dump_traceback_cfg := debug.dump_traceback) is None:
        return None

    file = _get_file_path(0)
    logging.getLogger('HABApp').info(f'Dumping traceback to {file}')

    # rotate files
    keep = 3
    _get_file_path(keep).unlink(missing_ok=True)
    for i in range(keep - 1, -1, -1):
        src = _get_file_path(i)
        if not src.is_file():
            continue

        dst = _get_file_path(i + 1)
        dst.unlink(missing_ok=True)
        src.rename(dst)

    task = create_task(
        dump_traceback_task(
            file, int(dump_traceback_cfg.delay.total_seconds()), int(dump_traceback_cfg.interval.total_seconds())
        ),
        name='DumpTracebackTask'
    )

    HABApp.core.shutdown.register(task.cancel, msg='Stopping traceback task')


async def dump_traceback_task(file: Path, delay: int, interval: int) -> None:

    with file.open('a') as f:
        f.write(f'Start: {datetime.now()}\n')
        f.write(f'Delay: {delay:d}s Interval: {interval:d}s\n')

    await sleep(delay)

    while True:
        with file.open('a') as f:
            f.write(f'\n{"-" * 80}\n')
            f.write(f'{datetime.now()}\n\n')
            dump_traceback(f, all_threads=True)

        await sleep(interval)
