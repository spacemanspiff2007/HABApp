import asyncio
import typing
from asyncio import Task, ensure_future, sleep
from typing import Any, Awaitable, Callable, Optional


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

    def reset(self):
        if self.is_canceled:
            return None

        if self.task is not None:
            # only cancel if it is not run or canceled
            if not (self.task.done() or self.task.cancelled()):
                self.task.cancel()
            self.task = None

        # todo: rename to asyncio.create_task once we go py3.7 only
        self.task = ensure_future(self.__countdown())

    async def __countdown(self):
        try:
            await sleep(self.secs)
            await self.func()
        except asyncio.CancelledError:
            pass
