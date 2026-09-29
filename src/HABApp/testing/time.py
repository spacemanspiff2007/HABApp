import asyncio
from asyncio import Future
from datetime import timedelta
from typing import Final, NamedTuple, override

from whenever import Instant, OffsetDateTime, TimeDelta, ZonedDateTime
from whenever._utils import _TimePatch

from HABApp.core.lib.asyncio import AsyncioProvider


type TimeDeltaLike = float | TimeDelta | timedelta


def _get_secs_from_delta(diff: TimeDeltaLike) -> float:
    match diff:
        case TimeDelta():
            secs: Final = diff.total('seconds')
        case timedelta():
            secs: Final = diff.total_seconds()
        case int() | float():
            secs: Final = diff
        case _:
            raise TypeError()

    if secs < 0:
        msg = 'Can only go into the future, not backwards in time'
        raise ValueError(msg)

    return secs


class PatchedTimeHelper:
    def __init__(self, time_patch: _TimePatch) -> None:
        self._time_patch: Final = time_patch

    def advance(self, diff: TimeDeltaLike) -> None:
        secs: Final = _get_secs_from_delta(diff)
        if secs == 0:
            return None

        self._time_patch.shift(seconds=secs)
        return None

    def advance_to(self, target: Instant) -> None:
        return self.advance(
            (target - Instant.now()).total('seconds')
        )


class AsyncioTestingProvider(AsyncioProvider):
    __slots__ = ('_patched_time', '_pending')

    def __init__(self, patched_time: PatchedTimeHelper) -> None:
        super().__init__()
        self._pending: Final[list[tuple[Instant, Future]]] = []
        self._patched_time: Final = patched_time

    @staticmethod
    def _pending_sort(obj: tuple[Instant, Future]) -> Instant:
        return obj[0]

    @override
    async def sleep(self, target: Instant | TimeDelta | float) -> None:

        match target:
            case Instant():
                due_in: Final = target
            case TimeDelta():
                due_in: Final = Instant.now().add(seconds=target.total('seconds'))
            case _:
                due_in: Final = Instant.now().add(seconds=target)

        f: Final = Future()
        self._pending.append((due_in, f))
        self._pending.sort(key=self._pending_sort)
        await f

    async def advance_to(self, target: Instant) -> None:
        while self._pending and self._pending[0][0] <= target:
            due: Instant = self._pending[0][0]

            # Collect all futures with the same due date
            batch: list[Future] = []
            while self._pending and self._pending[0][0] == due:
                _, f = self._pending.pop(0)
                batch.append(f)

            # set the time accordingly
            self._patched_time.advance_to(due)

            # Wake them all
            for f in batch:
                # if we reschedule the future might get canceled
                if not f.cancelled():
                    f.set_result(None)

            await asyncio.sleep(0.05)


class TestingStartTimeOptions(NamedTuple):
    start: Instant | ZonedDateTime | OffsetDateTime
    keep_ticking: bool = False


class UserTimeControl:
    def __init__(self, asyncio: AsyncioTestingProvider) -> None:
        self._asyncio: Final = asyncio

    async def sleep(self) -> None:
        await self.advance_to(Instant.now())

    async def advance(self, diff: TimeDeltaLike) -> None:
        return await self.advance_to(
            Instant.now().add(seconds=_get_secs_from_delta(diff))
        )

    async def advance_to(self, target: Instant) -> None:
        if target < Instant.now():
            msg = 'Can only go into the future, not backwards in time'
            raise ValueError(msg)

        # if we created a task we need some time for it to start and get ready
        await asyncio.sleep(0)

        return await self._asyncio.advance_to(target)
