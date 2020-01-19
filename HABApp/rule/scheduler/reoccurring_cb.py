import typing
from datetime import timedelta

from .base import ScheduledCallbackBase, local_tz


class ReoccurringScheduledCallback(ScheduledCallbackBase):

    def __init__(self, callback, *args, **kwargs):
        super().__init__(callback, *args, **kwargs)
        self._interval: timedelta = None

    def _calculate_next_call(self):
        self._next_base += self._interval
        self.update_run_time()

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
        self._weekdays: typing.Set[int] = None

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
        self._next_base += timedelta(days=1)
        loc = self._next_base.astimezone(local_tz)
        while not loc.isoweekday() in self._weekdays:
            self._next_base += timedelta(days=1)
            loc = self._next_base.astimezone(local_tz)
        self.update_run_time()
