import asyncio
import typing
from asyncio import Task, sleep, run_coroutine_threadsafe, create_task
from typing import Any, Awaitable, Callable, Optional

from HABApp.core.const import loop


# todo: switch to time.monotonic for measurements instead of fixed sleep time

class PendingFuture:
    def __init__(self, future: Callable[[], Awaitable[Any]], secs: typing.Union[int, float]):
        assert asyncio.iscoroutinefunction(future), type(future)
        if not isinstance(secs, (int, float)) or secs < 0:
            raise ValueError(f'Pending time must be int/float and >= 0! Is: {secs} ({type(secs)})')

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
        await sleep(self.secs)
        await self.func()
