from __future__ import annotations

from datetime import datetime as dt_datetime
from datetime import timedelta as dt_timedelta
from operator import ge, gt, le, lt
from typing import TYPE_CHECKING, Any, Final, TypeAlias, overload

from whenever import Instant, TimeDelta


if TYPE_CHECKING:
    from collections.abc import Callable


class InstantView:
    __slots__ = ('_instant', )

    def __init__(self, instant: Instant) -> None:
        self._instant: Final = instant

    @classmethod
    def now(cls) -> InstantView:
        """Create a new instance with the current time"""
        return cls(Instant.now())

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
        return self._instant.to_system_tz().local().py_datetime()

    def __repr__(self) -> str:
        return f'InstantView({self._instant.to_system_tz()})'

    def _cmp(self, op: Callable[[Any, Any], bool], obj: HINT_OBJ | None, **kwargs: float) -> bool:

        td: TimeDelta | None = None

        match obj:
            case None:
                if days := kwargs.get('days', 0):
                    kwargs['hours'] = kwargs.get('hours', 0) + days * 24
                td = TimeDelta(**kwargs)
            case TimeDelta():
                td = obj
            case dt_timedelta():
                td = TimeDelta.from_py_timedelta(obj)
            case int():
                td = TimeDelta(seconds=obj)
            case str():
                td = TimeDelta.parse_common_iso(obj)

        if td is None:
            if isinstance(obj, InstantView):
                obj = obj._instant
            if isinstance(obj, Instant):
                # If the compare the instant the logic is the other way around
                # view > delta(3)    -> view older than 3 seconds
                # view > instant(-3) -> view newer than the instant 3 seconds ago
                return {ge: le, gt: lt, le: ge, lt: gt}[op](self._instant, obj)

        if td is None:
            msg = f'Invalid type: {type(obj).__name__}'
            raise TypeError(msg)

        if td <= TimeDelta.ZERO:
            msg = 'Delta must be positive since instant is in the past'
            raise ValueError(msg)

        return op(self._instant, Instant.now() - td)

    @overload
    def older_than(self, *, days: float = 0, hours: float = 0, minutes: float = 0, seconds: float = 0) -> bool: ...
    @overload
    def older_than(self, obj: HINT_OBJ) -> bool: ...

    def older_than(self, obj=None, **kwargs):
        """Check if the instant is older than the given value"""
        return self._cmp(lt, obj, **kwargs)

    @overload
    def newer_than(self, *, days: float = 0, hours: float = 0, minutes: float = 0, seconds: float = 0) -> bool: ...
    @overload
    def newer_than(self, obj: HINT_OBJ) -> bool: ...

    def newer_than(self, obj=None, **kwargs):
        """Check if the instant is newer than the given value"""
        return self._cmp(gt, obj, **kwargs)

    def __lt__(self, other: HINT_OBJ) -> bool:
        return self._cmp(gt, other)

    def __le__(self, other: HINT_OBJ) -> bool:
        return self._cmp(ge, other)

    def __gt__(self, other: HINT_OBJ) -> bool:
        return self._cmp(lt, other)

    def __ge__(self, other: HINT_OBJ) -> bool:
        return self._cmp(le, other)

    def __eq__(self, other: InstantView | Instant) -> bool:
        if isinstance(other, InstantView):
            return self._instant == other._instant
        if isinstance(other, Instant):
            return self._instant == other
        return NotImplemented


HINT_OBJ: TypeAlias = dt_timedelta | TimeDelta | int | str | Instant | InstantView
