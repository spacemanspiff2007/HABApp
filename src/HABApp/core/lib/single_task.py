from asyncio import Task, CancelledError
from typing import Callable, Awaitable, Any, Final, Optional

from HABApp.core.const import loop

_TASK_REFS = set()


class SingleTask:
    def __init__(self, coro: Callable[[], Awaitable[Any]], name: Optional[str] = None):
        if name is None:
            name = f'{self.__class__.__name__}_{coro.__name__}'

        self.coro: Final = coro
        self.name: Final = name
        self.task: Optional[Task] = None

    @property
    def is_running(self) -> bool:
        return self.task is not None

    def cancel(self) -> Optional[Task]:
        if (task := self.task) is None:
            return None

        self.task = None

        # we need the reference only when we cancel a task, otherwise the task is saved in the attribute
        _TASK_REFS.add(task)
        task.add_done_callback(_TASK_REFS.discard)

        task.cancel()
        return task

    async def cancel_wait(self):
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

    def start(self, /, run_wrapped=True) -> Task:
        self.cancel()
        self.task = task = loop.create_task(self._task_wrap() if run_wrapped else self.coro(), name=self.name)
        return task

    def start_if_not_running(self, /, run_wrapped=True) -> Task:
        if (task := self.task) is not None:
            return task

        self.task = task = loop.create_task(self._task_wrap() if run_wrapped else self.coro(), name=self.name)
        return task

    async def _task_wrap(self):
        # don't use try-finally because this also runs on asyncio.CancelledError
        try:
            await self.coro()
        except Exception:
            pass

        self.task = None
