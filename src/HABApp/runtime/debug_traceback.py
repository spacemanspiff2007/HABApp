from __future__ import annotations

import asyncio
import faulthandler
import gc
import logging
import signal
import traceback
from asyncio import sleep
from datetime import datetime
from types import AsyncGeneratorType, FrameType
from typing import TYPE_CHECKING, Any, Final, TextIO

from HABApp.config.logging import rotate_file
from HABApp.core.lib import format_exception
from HABApp.core.wrapper import log_exception


if TYPE_CHECKING:
    from collections.abc import Callable

    from HABApp.config import ApplicationConfig


log = logging.getLogger('HABApp')


class DebugTraceback:
    def __init__(self) -> None:
        self.app_config: ApplicationConfig | None = None
        self._tb_file: TextIO | None = None
        self._tasks: tuple[asyncio.Task, ...] = ()

    async def shutdown(self) -> None:
        tasks = self._tasks
        self._tasks = ()

        if tasks:
            log.debug('Shutting down debug tasks')

            for task in tasks:
                task.cancel()

            for task in tasks:
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    for line in format_exception(e):
                        log.error(line)

        # close file last
        if (tb_file := self._tb_file) is not None:
            log.debug('Closing debug file')
            self._tb_file = None
            # todo: remove _dump_tasks_overview
            _dump_tasks_overview(tb_file)
            tb_file.close()

        return None

    def setup(self, config: ApplicationConfig) -> None:
        self.app_config = config
        config.habapp.debug.subscribe_for_changes(self._setup)

    @log_exception
    async def _setup(self) -> None:
        if self.app_config is None:
            return None

        await self.shutdown()

        # unregister signal handler - only works on some platforms, so we ignore possible AttributeError
        try:
            faulthandler.unregister(signal.SIGINT)
            faulthandler.unregister(signal.SIGTERM)
        except AttributeError:
            pass

        debug: Final = self.app_config.habapp.debug
        dump_thread_cfg: Final = debug.dump_threads
        dump_task_cfg: Final = debug.dump_tasks
        event_loop_cfg: Final = debug.watch_event_loop
        tb_on_shutdown_signal: Final = debug.dump_threads_on_shutdown_signal

        if (not event_loop_cfg.enabled and not tb_on_shutdown_signal and
                not dump_thread_cfg.enabled and not dump_task_cfg.enabled):
            return None

        file: Final = self.app_config.directories.logging / 'HABApp_traceback.log'
        log.info(f'Dumping traceback to {file}')

        rotate_file(file, 3)

        log.debug('Opening debug file')
        self._tb_file = file.open('a')

        if dump_thread_cfg.enabled:
            task = asyncio.create_task(
                periodic_dump_task(
                    what='threads',
                    file=self._tb_file,
                    delay=int(dump_thread_cfg.delay.total_seconds()),
                    interval=int(dump_thread_cfg.interval.total_seconds()),
                    func=faulthandler.dump_traceback,
                    all_threads=True
                ),
                name='DumpThreadsTask'
            )
            self._tasks += (task,)

        if dump_task_cfg.enabled:
            task = asyncio.create_task(
                periodic_dump_task(
                    what='tasks',
                    file=self._tb_file,
                    delay=int(dump_thread_cfg.delay.total_seconds()),
                    interval=int(dump_thread_cfg.interval.total_seconds()),
                    func=_dump_tasks_overview,
                ),
                name='DumpAsyncioTasksTask'
            )
            self._tasks += (task,)

        if event_loop_cfg.enabled:
            task = asyncio.create_task(
                watch_event_loop_task(
                    file=self._tb_file,
                    sleep_secs=int(event_loop_cfg.reset_every.total_seconds()),
                    timeout_secs=int(event_loop_cfg.timeout.total_seconds()),
                ),
                name='WatchEventLoopTask'
            )
            self._tasks += (task,)

        if tb_on_shutdown_signal:
            self._tb_file.write('Dumping on shutdown signal\n')
            self._tb_file.flush()

            faulthandler.register(signal.SIGINT, self._tb_file, all_threads=True)
            faulthandler.register(signal.SIGTERM, self._tb_file, all_threads=True)

        return None


def _get_frame(obj: Any) -> FrameType | None:
    return (
        getattr(obj, 'cr_frame', None)
        or getattr(obj, 'gi_frame', None)
        or getattr(obj, 'ag_frame', None)
    )


def _get_awaited(obj: Any):  # noqa: ANN202
    return (
        getattr(obj, 'cr_await', None)
        or getattr(obj, 'gi_yieldfrom', None)
        or getattr(obj, 'ag_await', None)
    )


def _resolve_awaited(awaited: Any) -> Any:
    """Return a coroutine/generator/async-gen to descend into, or None."""
    # native coroutine or generator - descend directly
    if _get_frame(awaited) is not None:
        return awaited

    # a Task/Future wrapping another coroutine -> descend into the coro
    if isinstance(awaited, asyncio.Task):
        return awaited.get_coro()

    # async_generator_asend / athrow wrapper -> find wrapped async generator
    type_name = type(awaited).__name__
    if type_name in ('async_generator_asend', 'async_generator_athrow'):
        for ref in gc.get_referents(awaited):
            if isinstance(ref, AsyncGeneratorType):
                return ref

    return None


def _format_task_stack(task: asyncio.Task) -> list[str]:
    lines: list[str] = []

    obj = task.get_coro()
    while obj is not None:
        frame = _get_frame(obj)
        if frame is None:
            break

        lines.extend(traceback.format_list(traceback.extract_stack(frame, limit=1)))

        obj = _resolve_awaited(_get_awaited(obj))

    return lines


def _dump_tasks_overview(file: TextIO) -> None:

    lines: list[str] = []

    for task in asyncio.all_tasks():
        try:
            done = task.done()
            cancelled = task.cancelled()

            # Status bestimmen
            if cancelled:
                status = 'CANCELLED'
            elif done:
                status = 'DONE'
            else:
                status = 'RUNNING'

            lines.append(f'{task.get_name():<20} [{status:s}]\n')

            # Traceback für nicht-abgeschlossene Tasks anzeigen
            if done or cancelled:
                continue

            tb_lines = _format_task_stack(task)
            lines.extend(tb_lines)
            lines.append('\n')

        except Exception as e:
            lines.append(f'  Error getting traceback: {e}\n\n')

    file.writelines(lines)


@log_exception
async def periodic_dump_task(what: str, file: TextIO, delay: int, interval: int,
                             func: Callable, **kwargs: Any) -> None:

    file.write(
        f'Dumping {what:s}\n'
        f'Start: {datetime.now()}\n'
        f'Delay: {delay:d}s Interval: {interval:d}s\n'
        f'{"-" * 80}\n\n'
    )
    file.flush()

    await sleep(delay)

    while True:
        file.write(f'{datetime.now()}\n\n')
        func(file, **kwargs)
        file.write(f'\n{"-" * 80}\n')
        file.flush()

        await sleep(interval)


@log_exception
async def watch_event_loop_task(file: TextIO, sleep_secs: int, timeout_secs: int) -> None:

    file.write(
        f'Watching event loop\n'
        f'Reset: {sleep_secs:d}s Timeout: {timeout_secs:d}s\n'
        f'{"-" * 80}\n\n'
    )
    file.flush()

    while True:
        faulthandler.dump_traceback_later(timeout_secs, file=file, exit=True)
        await sleep(sleep_secs)
