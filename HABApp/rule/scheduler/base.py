import random
import typing
import tzlocal
from datetime import datetime, timedelta, time

from pytz import utc

from HABApp.core import WrappedFunction

TYPING_DATE_TIME = typing.Union[None, datetime, timedelta, time]

local_tz = tzlocal.get_localzone()


def replace_time(dt_obj: datetime, t_obj: typing.Union[datetime, time]) -> datetime:
    return dt_obj.replace(hour=t_obj.hour, minute=t_obj.minute, second=t_obj.second, microsecond=0)


class ScheduledCallbackBase:

    def __init__(self, callback: WrappedFunction, *args, **kwargs):

        self._callback: WrappedFunction = callback
        self._args = args
        self._kwargs = kwargs

        # boundaries
        self._earliest: typing.Optional[time] = None
        self._latest: typing.Optional[time] = None
        self._offset: typing.Optional[timedelta] = None
        self._jitter: typing.Optional[int] = None
        self._boundary_func: typing.Optional[typing.Callable[[datetime], datetime]] = None

        # times when we run
        self._next_base: datetime
        self._next_call: datetime

        # properties
        self.is_due = False
        self.is_finished = False
        self.run_counter = 0

    def _set_next_base(self, next_time: TYPING_DATE_TIME) -> 'ScheduledCallbackBase':
        # initializer method for self._next_base

        __now = datetime.now()
        if next_time is None:
            # If we don't specify a datetime we start it now
            base_time = __now
        elif isinstance(next_time, timedelta):
            # if it is a timedelta add it to now to easily speciy points in the future
            base_time = __now + next_time
        elif isinstance(next_time, time):
            # if it is a time object it specifies a time of day.
            base_time = __now.replace(hour=next_time.hour, minute=next_time.minute, second=next_time.second)
            if base_time < __now:
                base_time += timedelta(days=1)
        else:
            base_time = next_time

        assert isinstance(base_time, datetime), type(base_time)

        # convert to utc
        base_time = local_tz.localize(base_time)
        self._next_base = base_time.astimezone(utc)
        return self

    def _calculate_next_call(self):
        """Get next calc time"""
        raise NotImplementedError()

    def earliest(self, time_obj: typing.Optional[time]) -> 'ScheduledCallbackBase':
        """Set earliest boundary as time of day. ``None`` will disable boundary.

        :param time_obj: time obj, scheduler will not run earlier
        """
        assert isinstance(time_obj, time) or time_obj is None, type(time_obj)
        changed = self._earliest != time_obj
        self._earliest = time_obj
        if changed:
            self._update_run_time()
        return self

    def latest(self, time_obj: typing.Optional[time]) -> 'ScheduledCallbackBase':
        """Set earliest boundary as time of day. ``None`` will disable boundary.

        :param time_obj: time obj, scheduler will not run later
        """
        assert isinstance(time_obj, time) or time_obj is None, type(time_obj)
        changed = self._latest != time_obj
        self._latest = time_obj
        if changed:
            self._update_run_time()
        return self

    def offset(self, timedelta_obj: typing.Optional[timedelta]) -> 'ScheduledCallbackBase':
        """Set a constant offset to the calculation of the next run. ``None`` will disable the offset.

        :param timedelta_obj: constant offset
        """
        assert isinstance(timedelta_obj, timedelta) or timedelta_obj is None, type(timedelta_obj)
        changed = self._offset != timedelta_obj
        self._offset = timedelta_obj
        if changed:
            self._update_run_time()
        return self

    def jitter(self, secs: typing.Optional[int]) -> 'ScheduledCallbackBase':
        """Add a random jitter per call in the intervall [(-1) * secs ... secs] to the next run.
         ``None`` will disable jitter.

        :param secs: jitter in secs
        """
        assert isinstance(secs, int) or secs is None, type(secs)
        changed = self._jitter != secs
        self._jitter = secs
        if changed:
            self._update_run_time()
        return self

    def boundary_func(self, func: typing.Optional[typing.Callable[[datetime], datetime]]):
        """Add a function which will be called when the datetime changes. Use this to implement custom boundaries.
         Use ``None`` to disable the boundary function.

        :param func: Function which returns a datetime obj, arg is a datetime with the next call time
        """
        changed = self._boundary_func != func
        self._boundary_func = func
        if changed:
            self._update_run_time()
        return self

    def _update_run_time(self) -> 'ScheduledCallbackBase':
        # Starting point is always the next call
        self._next_call = self._next_base

        # custom boundaries first
        if self._boundary_func is not None:
            self._next_call = self._boundary_func(self._next_call.astimezone(local_tz)).astimezone(utc)

        if self._offset is not None:
            self._next_call += self._offset  # offset doesn't have to be localized

        if self._jitter is not None:
            self._next_call += timedelta(seconds=random.randint(-1 * self._jitter, self._jitter))

        if self._earliest is not None:
            earliest = replace_time(self._next_call.astimezone(local_tz), self._earliest)
            earliest = earliest.astimezone(utc)
            if self._next_call < earliest:
                self._next_call = earliest

        if self._latest is not None:
            latest = replace_time(self._next_call.astimezone(local_tz), self._latest)
            latest = latest.astimezone(utc)
            if self._next_call > latest:
                self._next_call = latest

        return self

    def get_next_call(self):
        """Return the next execution timestamp"""
        return self._next_call.astimezone(local_tz).replace(tzinfo=None)

    def check_due(self, now: datetime):
        """Check whether the callback is due for execution

        :param now:
        :return:
        """

        self.is_due = True if self._next_call <= now else False
        if self.is_finished:
            self.is_due = False

        return self.is_due

    def execute(self) -> bool:
        """Try to execute callback. If the callback is not due yet or execution has already finished nothing will happen

        :return: True if callback has been executed else False
        """
        if not self.is_due or self.is_finished:
            return False

        self.run_counter += 1
        self._calculate_next_call()
        self._callback.run(*self._args, **self._kwargs)
        return True

    def cancel(self):
        """Cancel execution
        """
        self.is_finished = True
