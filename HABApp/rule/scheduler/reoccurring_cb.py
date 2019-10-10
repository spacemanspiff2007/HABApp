import typing
import datetime

from .scheduled_cb import ScheduledCallback, TYPING_DATE_TIME


class ReoccurringScheduledCallback(ScheduledCallback):

    CALL_ONCE = False

    def __init__(
            self, time: TYPING_DATE_TIME, interval: typing.Union[int, datetime.timedelta], callback, *args, **kwargs):
        super().__init__(time, callback, *args, **kwargs)

        if isinstance(interval, int):
            interval = datetime.timedelta(seconds=interval)
        assert isinstance(interval, datetime.timedelta), type(interval)
        self.time_interval = interval

    def check_due(self, now: datetime):
        super().check_due(now)
        if self.is_due:
            self.next_call += self.time_interval


class DayOfWeekScheduledCallback(ScheduledCallback):

    CALL_ONCE = False

    def __init__(self, time: TYPING_DATE_TIME, weekdays: typing.List[int], callback, *args, **kwargs):
        super().__init__(time, callback, *args, **kwargs)

        assert weekdays, 'please specify weekdays'
        assert isinstance(weekdays, list)
        for k in weekdays:
            assert 1 <= k <= 7, k
        self.weekdays = weekdays

        # shedule for next day if the date_time is in the past or date does not match weekdays
        while not self.next_call.isoweekday() in self.weekdays:
            self.next_call += datetime.timedelta(days=1)

    def check_due(self, now: datetime):
        super().check_due(now)
        if self.is_due:
            self.next_call += datetime.timedelta(days=1)
            while not self.next_call.isoweekday() in self.weekdays:
                self.next_call += datetime.timedelta(days=1)


class WorkdayScheduledCallback(DayOfWeekScheduledCallback):
    def __init__(self, time: TYPING_DATE_TIME, callback, *args, **kwargs):
        super().__init__(time, [1, 2, 3, 4, 5], callback, *args, **kwargs)


class WeekendScheduledCallback(DayOfWeekScheduledCallback):
    def __init__(self, time: TYPING_DATE_TIME, callback, *args, **kwargs):
        super().__init__(time, [6, 7], callback, *args, **kwargs)
