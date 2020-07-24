import asyncio
import typing
from asyncio import Task, sleep, ensure_future
from typing import Optional, Union, Coroutine


class PendingFuture:
    def __init__(self, future: Coroutine, secs: typing.Union[int, float]):
        assert isinstance(future, Coroutine), type(future)
        assert isinstance(secs, (int, float)), type(secs)

        self.secs = secs
        self.func: Union[Coroutine] = future
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
            await self.func
        except asyncio.CancelledError:
            pass
