from asyncio import CancelledError, Task, current_task
from collections.abc import Awaitable, Callable
from typing import Any, Final

from HABApp.core.const import loop


_TASK_REFS = set()


class SingleTask:
    def __init__(self, coro: Callable[[], Awaitable[Any]], name: str | None = None) -> None:
        if name is None:
            name = f'{self.__class__.__name__}_{coro.__name__}'

        self.coro: Final = coro
        self.name: Final = name
        self.task: Task | None = None

    @property
    def is_running(self) -> bool:
        return self.task is not None

    def cancel(self) -> Task | None:
        if (task := self.task) is None:
            return None

        self.task = None

        # we need the reference only when we cancel a task, otherwise the task is saved in the attribute
        _TASK_REFS.add(task)
        task.add_done_callback(_TASK_REFS.discard)

        task.cancel()
        return task

    async def cancel_wait(self) -> None:
        if task := self.cancel():
            try:
                await task
            except CancelledError:
                pass

    async def wait(self):
        if self.task is None:
            return None

        try:
            await self.task
        except CancelledError:
            pass

    def start(self) -> Task:
        self.cancel()
        self.task = task = loop.create_task(self._task_wrap(), name=self.name)
        return task

    def start_if_not_running(self) -> Task:
        if (task := self.task) is not None:
            return task

        self.task = task = loop.create_task(self._task_wrap(), name=self.name)
        return task

    async def _task_wrap(self) -> None:
        task = current_task(loop)

        # don't use try-finally because
        try:
            await self.coro()
        finally:
            # This also runs on asyncio.CancelledError so we have to make sure it's the same task
            if self.task is task:
                self.task = None
