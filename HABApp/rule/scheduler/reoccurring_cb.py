import typing
from datetime import datetime, time, timedelta

from pytz import utc

from .base import ScheduledCallbackBase, local_tz


class ReoccurringScheduledCallback(ScheduledCallbackBase):

    def __init__(self, callback, *args, **kwargs):
        super().__init__(callback, *args, **kwargs)
        self._interval: timedelta = None

    def _calculate_next_call(self):
        self._next_base += self._interval
        self._update_run_time()

    def interval(self, interval: typing.Union[int, timedelta]) -> 'ReoccurringScheduledCallback':
        if isinstance(interval, int):
            interval = timedelta(seconds=interval)
        assert isinstance(interval, timedelta), type(interval)
        assert interval.total_seconds() > 0
        self._interval = interval
        return self


class DayOfWeekScheduledCallback(ScheduledCallbackBase):

    def __init__(self, callback, *args, **kwargs):
        super().__init__(callback, *args, **kwargs)
        self._time: time = None
        self._weekdays: typing.Set[int] = None

    def set_next_run_time(self, _time: time) -> 'DayOfWeekScheduledCallback':
        assert isinstance(_time, time), type(_time)
        self._time = _time
        super().set_next_run_time(_time)

        return self

    def weekdays(self, weekdays) -> 'DayOfWeekScheduledCallback':
        if weekdays == 'weekend':
            weekdays = [6, 7]
        elif weekdays == 'workday':
            weekdays = [1, 2, 3, 4, 5]
        for k in weekdays:
            assert 1 <= k <= 7, k
        self._weekdays = weekdays
        return self

    def _calculate_next_call(self):

        # we have to do it like this so the dst-change works,
        # otherwise we have the wrong hour after the change
        next_date = self._next_base.date() + timedelta(days=1)
        loc = datetime.combine(next_date, self._time, tzinfo=local_tz)

        while not loc.isoweekday() in self._weekdays:
            next_date += timedelta(days=1)
            loc = datetime.combine(next_date, self._time, tzinfo=local_tz)

        self._next_base = loc.astimezone(utc)
        self._update_run_time()
