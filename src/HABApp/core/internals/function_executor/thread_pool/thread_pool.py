from __future__ import annotations

import asyncio
import logging
from asyncio import get_event_loop
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import TYPE_CHECKING, Final, Self

from HABApp.core.asyncio import thread_context


if TYPE_CHECKING:
    from HABApp.config import ApplicationConfig
    from HABApp.core.internals.function_executor.thread_pool.pool_function import PoolFunction


log = logging.getLogger('HABApp.ThreadPool')


def _initialize_thread() -> None:
    thread_context.set('HABAppWorker')


class HABAppThreadPool:
    __slots__ = ('_executor', '_lock_pending', '_lock_running', '_pending', '_running', 'max_workers')

    @classmethod
    def create(cls, config: ApplicationConfig) -> Self:
        executor, max_workers = cls.create_thread_pool_executor(config)
        return cls(executor, max_workers)

    @staticmethod
    def create_thread_pool_executor(config: ApplicationConfig) -> tuple[ThreadPoolExecutor, int]:
        max_workers = config.habapp.thread_pool.threads
        log.debug(f'Creating ThreadPoolExecutor with {max_workers:d} threads')
        return (
            ThreadPoolExecutor(
                max_workers=max_workers,
                thread_name_prefix='HABAppWorker',
                initializer=_initialize_thread
            ),
            max_workers
        )

    @staticmethod
    async def shutdown_thread_pool_executor(executor: ThreadPoolExecutor) -> None:
        log.debug('Shutting down')
        fut = get_event_loop().run_in_executor(None, executor.shutdown)
        try:
            await asyncio.wait_for(fut, timeout=5)
        except TimeoutError:
            log.error('Timeout while waiting for shutdown! Are you using long running threads?')

    def __init__(self, executor: ThreadPoolExecutor, max_workers: int) -> None:
        self._executor: ThreadPoolExecutor = executor
        self.max_workers: int = max_workers

        self._lock_running: Final = Lock()
        self._running: Final[set[PoolFunction]] = set()

        self._lock_pending: Final = Lock()
        self._pending: Final[set[PoolFunction]] = set()

    async def update_executor(self, config: ApplicationConfig) -> ThreadPoolExecutor:
        executor = self._executor
        self._executor, self.max_workers = self.create_thread_pool_executor(config)
        return executor

    async def shutdown(self) -> None:
        await self.shutdown_thread_pool_executor(self._executor)
        return None

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} pending={len(self._pending):s} running={len(self._running):d}>'

    def func_start(self, func: PoolFunction) -> None:
        with self._lock_pending:
            self._pending.discard(func)

        running = self._running
        with self._lock_running:
            running.add(func)

            count = len(running)
            for info in running:
                info.usage_high = max(count, info.usage_high)

    def func_complete(self, func: PoolFunction) -> None:
        with self._lock_running:
            self._running.discard(func)

    def submit(self, func: PoolFunction) -> None:
        with self._lock_pending:
            self._pending.add(func)

        self._executor.submit(func.run)
        return None
