from asyncio import AbstractEventLoop, Task, create_task, run_coroutine_threadsafe, sleep
from collections.abc import Awaitable, Callable
from inspect import iscoroutinefunction
from typing import Any, Final


# TODO: switch to time.monotonic for measurements instead of fixed sleep time

class PendingFuture:
    def __init__(self, future: Callable[[], Awaitable[Any]], secs: float) -> None:
        assert iscoroutinefunction(future), type(future)

        if not isinstance(secs, (int, float)) or secs < 0:
            msg = f'Pending time must be int/float and >= 0! Is: {secs} ({type(secs)})'
            raise ValueError(msg)

        self.func: Callable[[], Awaitable[Any]] = future
        self.secs: Final = secs
        self.task: Task | None = None

        self.is_canceled: bool = False

    def cancel(self) -> None:
        self.is_canceled = True

        if (t := self.task) is not None:
            self.task = None

            # only cancel if it is not run or canceled
            if not (t.done() or t.cancelled()):
                t.cancel()

    def reset(self, *, loop: AbstractEventLoop | None = None) -> None:
        if self.is_canceled:
            return None

        if (t := self.task) is not None:
            self.task = None
            # only cancel if it is not run or canceled
            if not (t.done() or t.cancelled()):
                t.cancel()

        if loop is None:
            self.task = create_task(self.__countdown())
        else:
            self.task = run_coroutine_threadsafe(self.__countdown(), loop)
        return None

    async def __countdown(self) -> None:
        await sleep(self.secs)
        await self.func()
