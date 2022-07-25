from asyncio import create_task, Task
from typing import Callable, Awaitable, Any, Final, Optional


class SingleTask:
    def __init__(self, coro: Callable[[], Awaitable[Any]], name: Optional[str] = None):
        if name is None:
            name = f'{self.__class__.__name__}_{coro.__name__}'

        self.coro: Final = coro
        self.task: Optional[Task] = None
        self.name: Final = name

    def cancel(self):
        if self.task is not None:
            task = self.task
            self.task = None
            task.cancel()

    def start(self):
        self.cancel()
        self.task = create_task(self._task_wrap(), name=self.name)

    async def _task_wrap(self):
        # don't use try-finally because this also catches the asyncio.CancelledError
        try:
            await self.coro()
        except Exception:
            pass

        self.task = None
