from datetime import datetime, timedelta

from .scheduled_cb import ScheduledCallback


class ReoccuringScheduledCallback(ScheduledCallback):

    def __init__(self, date_time, interval, callback, *args, **kwargs):
        super().__init__(date_time, callback, *args, **kwargs)

        if isinstance(interval, int):
            interval = timedelta(seconds=interval)
        assert isinstance(interval, timedelta), type(interval)
        self.time_interval = interval

    def check_due(self, now: datetime):
        super().check_due(now)
        if self.is_due:
            self.next_call += self.time_interval
        self.is_finished = False


class DayOfWeekScheduledCallback(ScheduledCallback):
    def __init__(self, datetime_time, weekdays, callback, *args, **kwargs):
        super().__init__(datetime_time, callback, *args, **kwargs)

        assert weekdays, 'please specify weekdays'
        assert isinstance(weekdays, list)
        for k in weekdays:
            assert 1 <= k <= 7, k
        self.weekdays = weekdays

        # shedule for next day if the date_time is in the past or date does not match weekdays
        while not self.next_call.isoweekday() in self.weekdays:
            self.next_call += timedelta(days=1)

    def check_due(self, now: datetime):
        super().check_due(now)
        self.is_finished = False
        if self.is_due:
            self.next_call += timedelta(days=1)
            while not self.next_call.isoweekday() in self.weekdays:
                self.next_call += timedelta(days=1)


class WorkdayScheduledCallback(DayOfWeekScheduledCallback):
    def __init__(self, datetime_time, callback, *args, **kwargs):
        super().__init__(datetime_time, callback, *args, weekdays=[1, 2, 3, 4, 5], **kwargs)


class WeekendScheduledCallback(DayOfWeekScheduledCallback):
    def __init__(self, datetime_time, callback, *args, **kwargs):
        super().__init__(datetime_time, callback, *args, weekdays=[6, 7], **kwargs)
