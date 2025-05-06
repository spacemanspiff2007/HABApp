from __future__ import annotations

from operator import gt, lt
from typing import TYPE_CHECKING, Final, TypeAlias, overload

from eascheduler.builder.helper import HINT_TIMEDELTA, get_timedelta
from typing_extensions import Self
from whenever import Instant, TimeDelta


if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import datetime as dt_datetime
    from datetime import timedelta as dt_timedelta


class InstantView:
    __slots__ = ('_instant', )

    def __init__(self, instant: Instant) -> None:
        self._instant: Final = instant

    @classmethod
    def now(cls) -> InstantView:
        """Create a new instance with the current time"""
        return cls(Instant.now())

    def add(self, *, hours: float = 0, minutes: float = 0, seconds: float = 0,
            milliseconds: float = 0, microseconds: float = 0, nanoseconds: int = 0) -> Self:
        """Add time delta

        :return: New instance
        """
        return self.__class__(self._instant + TimeDelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=milliseconds,
            microseconds=microseconds,
            nanoseconds=nanoseconds,
        ))

    def subtract(self, *, hours: float = 0, minutes: float = 0, seconds: float = 0,
                 milliseconds: float = 0, microseconds: float = 0, nanoseconds: int = 0) -> Self:
        """Subtract time delta from current instant

        :return: New instance
        """
        return self.__class__(self._instant + TimeDelta(
            hours=-hours,
            minutes=-minutes,
            seconds=-seconds,
            milliseconds=-milliseconds,
            microseconds=-microseconds,
            nanoseconds=-nanoseconds,
        ))

    def delta_now(self, now: InstantView | Instant | None = None) -> TimeDelta:
        """Return the delta between now and the instant.
        The delta will be positive, e.g.
        if the InstantView is from 5 seconds ago this will return a timedelta with 5 seconds.

        :param now: optional instant to compare to instead of now, must be newer than the instant of the instant view
        """

        match now:
            case None:
                ref = Instant.now()
            case InstantView():
                ref = now._instant
            case Instant():
                ref = now
            case _:
                msg = f'Invalid type: {type(now).__name__}'
                raise TypeError(msg)

        if ref < self._instant:
            msg = f'Reference instant must be newer than the instant of the {self.__class__.__name__}'
            raise ValueError(msg)

        return ref - self._instant

    def py_timedelta(self, now: InstantView | Instant | None = None) -> dt_timedelta:
        """Return the timedelta between the instant and now

        :param now: optional instant to compare to
        """
        return self.delta_now(now).py_timedelta()

    def py_datetime(self) -> dt_datetime:
        """Return the datetime of the instant"""
        return self._instant.to_system_tz().to_plain().py_datetime()

    def __repr__(self) -> str:
        return f'InstantView({self._instant.to_system_tz()})'

    def _cmp(self, op: Callable[[Instant, Instant], bool], obj: HINT_OBJ | None, *,
             delta_kwargs: dict[str, float] | None = None) -> bool:

        match obj:
            case None:
                if days := delta_kwargs.pop('days', 0):
                    delta_kwargs['hours'] = delta_kwargs.get('hours', 0) + days * 24
                td = TimeDelta(**delta_kwargs)
            case InstantView():
                return op(self._instant, obj._instant)
            case Instant():
                return op(self._instant, obj)
            case _:
                td = get_timedelta(obj)

        if td <= TimeDelta.ZERO:
            msg = 'Delta must be positive since instant is in the past'
            raise ValueError(msg)

        return op(self._instant, Instant.now() - td)

    @overload
    def older_than(self, *, days: float = 0, hours: float = 0, minutes: float = 0, seconds: float = 0,
                   milliseconds: float = 0, microseconds: float = 0, nanoseconds: int = 0) -> bool: ...

    @overload
    def older_than(self, obj: HINT_OBJ) -> bool: ...

    def older_than(self, obj=None, **kwargs):
        """Check if the instant is older than the given value"""
        return self._cmp(lt, obj, delta_kwargs=kwargs)

    @overload
    def newer_than(self, *, days: float = 0, hours: float = 0, minutes: float = 0, seconds: float = 0,
                   milliseconds: float = 0, microseconds: float = 0, nanoseconds: int = 0) -> bool: ...

    @overload
    def newer_than(self, obj: HINT_OBJ) -> bool: ...

    def newer_than(self, obj=None, **kwargs):
        """Check if the instant is newer than the given value"""
        return self._cmp(gt, obj, delta_kwargs=kwargs)

    # ------------------------------------------------------------------------------------------------------------------
    # Comparisons
    def __lt__(self, other: InstantView | Instant) -> bool:
        if isinstance(other, InstantView):
            return self._instant < other._instant
        if isinstance(other, Instant):
            return self._instant < other
        return NotImplemented

    def __le__(self, other: InstantView | Instant) -> bool:
        if isinstance(other, InstantView):
            return self._instant <= other._instant
        if isinstance(other, Instant):
            return self._instant <= other
        return NotImplemented

    def __gt__(self, other: InstantView | Instant) -> bool:
        if isinstance(other, InstantView):
            return self._instant > other._instant
        if isinstance(other, Instant):
            return self._instant > other
        return NotImplemented

    def __ge__(self, other: InstantView | Instant) -> bool:
        if isinstance(other, InstantView):
            return self._instant >= other._instant
        if isinstance(other, Instant):
            return self._instant >= other
        return NotImplemented

    def __eq__(self, other: InstantView | Instant) -> bool:
        if isinstance(other, InstantView):
            return self._instant == other._instant
        if isinstance(other, Instant):
            return self._instant == other
        return NotImplemented

    # ------------------------------------------------------------------------------------------------------------------
    # Operations
    def __add__(self, other: HINT_TIMEDELTA) -> Self:
        """Add time delta to current instant

        :param other: time delta object
        :return: New instance
        """
        try:
            td = get_timedelta(other)
        except TypeError:
            return NotImplemented
        return self.__class__(self._instant + td)

    def __sub__(self, other: HINT_TIMEDELTA) -> Self:
        """Subtract time delta from current instant

        :param other: time delta object
        :return: New instance
        """
        try:
            td = get_timedelta(other)
        except TypeError:
            return NotImplemented
        return self.__class__(self._instant - td)


HINT_OBJ: TypeAlias = HINT_TIMEDELTA | Instant | InstantView
