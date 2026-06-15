from __future__ import annotations

import logging
from asyncio import AbstractEventLoop, Task, get_running_loop
from asyncio import create_task as _create_task
from asyncio import sleep as _sleep
from typing import TYPE_CHECKING, Any, Final, Self

from whenever import Instant, TimeDelta

from HABApp.core.lib.asyncio.single_task import SingleTask
from HABApp.core.provider import HABAPP_PROVIDER


if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine
    from types import TracebackType


@HABAPP_PROVIDER.register
class AsyncioProvider:
    __slots__ = ('_log', '_tasks', 'loop')

    def __init__(self, *, loop: AbstractEventLoop | None = None) -> None:
        self._tasks: Final[set[Task]] = set()
        self._log: Final = logging.getLogger('HABApp.asyncio')
        self.loop: Final[AbstractEventLoop] = loop if loop is not None else get_running_loop()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} tasks={len(self._tasks)}>'

    @staticmethod
    async def sleep(target: Instant | TimeDelta | float) -> None:

        match target:
            case Instant():
                delay: Final[float] = (target - Instant.now()).in_seconds()
            case TimeDelta():
                delay: Final[float] = target.in_seconds()
            case _:
                delay: Final[float] = target

        await _sleep(delay)

    def create_task[T](self, coro: Coroutine[Any, Any, T], *, name: str | None = None) -> Task[T]:
        task: Final = _create_task(coro, name=name)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None,
                        exc_tb: TracebackType | None) -> None:
        await self.wait_for_tasks()
        return None

    async def wait_for_tasks(self) -> None:

        started: Final = Instant.now()
        log_every: Final = 2
        wait_until: Final = started.add(seconds=10)

        next_log: Instant = started
        while self._tasks and Instant.now() < wait_until:
            if Instant.now() < next_log:
                await _sleep(0.2)
                continue

            next_log = next_log.add(seconds=log_every)

            names: list[str] = [t.get_name() for t in self._tasks]
            self._log.debug(f'Running tasks: {", ".join(names)}')

        if self._tasks:
            self._log.warning('Some tasks are still running:')
            for task in self._tasks:
                self._log.warning(f' - {task.get_name():s} done={task.done()}')

    def create_single_task(self, coro: Callable[[], Coroutine[Any, Any, Any]], name: str | None = None) -> SingleTask:
        return SingleTask(coro, name=name, asyncio=self)
