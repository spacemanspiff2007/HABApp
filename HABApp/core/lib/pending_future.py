import asyncio
import typing
from asyncio import Task, sleep, run_coroutine_threadsafe, create_task
from typing import Any, Awaitable, Callable, Optional
from HABApp.core.const import loop


class PendingFuture:
    def __init__(self, future: Callable[[], Awaitable[Any]], secs: typing.Union[int, float]):
        assert asyncio.iscoroutinefunction(future), type(future)
        assert isinstance(secs, (int, float)) and secs >= 0, f'{secs} ({type(secs)})'

        self.func: Callable[[], Awaitable[Any]] = future
        self.secs = secs
        self.task: Optional[Task] = None

        self.is_canceled: bool = False

    def cancel(self):
        self.is_canceled = True

        if self.task is not None:
            # only cancel if it is not run or canceled
            if not (self.task.done() or self.task.cancelled()):
                self.task.cancel()
            self.task = None

    def reset(self, thread_safe=False):
        if self.is_canceled:
            return None

        if self.task is not None:
            # only cancel if it is not run or canceled
            if not (self.task.done() or self.task.cancelled()):
                self.task.cancel()
            self.task = None

        if thread_safe:
            self.task = run_coroutine_threadsafe(self.__countdown(), loop)
        else:
            self.task = create_task(self.__countdown())

    async def __countdown(self):
        try:
            await sleep(self.secs)
            await self.func()
        except asyncio.CancelledError:
            pass
