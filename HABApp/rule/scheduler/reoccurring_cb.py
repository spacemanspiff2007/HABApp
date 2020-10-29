import typing
from datetime import datetime, time, timedelta

from pytz import utc

from .base import ScheduledCallbackBase, local_tz


class ReoccurringScheduledCallback(ScheduledCallbackBase):

    def __init__(self, callback, *args, **kwargs):
        super().__init__(callback, *args, **kwargs)
        self._interval: timedelta

    def _calculate_next_call(self):
        self._next_base += self._interval
        self._update_run_time()

    def interval(self, interval: typing.Union[int, timedelta]) -> 'ReoccurringScheduledCallback':
        if isinstance(interval, int):
            interval = timedelta(seconds=interval)
        assert isinstance(interval, timedelta), type(interval)
        assert interval.total_seconds() > 0

        self._interval = interval
        super()._set_next_base(interval)

        self._update_run_time()
        return self


class DayOfWeekScheduledCallback(ScheduledCallbackBase):

    def __init__(self, callback, *args, **kwargs):
        super().__init__(callback, *args, **kwargs)
        self._time: time
        self._weekdays: typing.Set[int]

    def time(self, _time: typing.Union[time, datetime]) -> 'DayOfWeekScheduledCallback':
        super()._set_next_base(_time)

        self._time = _time if isinstance(_time, time) else _time.time()

        # it is possible that the current day is not in the weekdays -> find next correct day
        # it's also why we don't have to call _update_run_time here
        self._calculate_next_call(add_day=False)
        return self

    def weekdays(self, weekdays) -> 'DayOfWeekScheduledCallback':
        if weekdays == 'weekend':
            weekdays = [6, 7]
        elif weekdays == 'workday':
            weekdays = [1, 2, 3, 4, 5]
        elif weekdays == 'all':
            weekdays = [1, 2, 3, 4, 5, 6, 7]
        for k in weekdays:
            assert 1 <= k <= 7, k
        self._weekdays = weekdays
        return self

    def _calculate_next_call(self, add_day=True):

        # we have to do it like this so the dst-change works,
        # otherwise we have the wrong hour after the change
        next_utc = self._next_base + timedelta(days=1) if add_day else self._next_base
        loc = datetime.combine(next_utc.astimezone(local_tz).date(), self._time)

        while not loc.isoweekday() in self._weekdays:
            loc += timedelta(days=1)

        self._next_base = loc.astimezone(utc)
        self._update_run_time()
