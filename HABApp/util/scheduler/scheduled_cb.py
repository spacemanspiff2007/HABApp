import typing
from datetime import datetime, timedelta, time

if typing.TYPE_CHECKING:
    from concurrent.futures import ThreadPoolExecutor

from concurrent.futures import ThreadPoolExecutor


class ScheduledCallback:

    def __init__(self, date_time, callback, *args, **kwargs):

        # next time the callback will be executed
        __now = datetime.now()

        if isinstance(date_time, int):
            date_time = __now + timedelta(seconds=date_time)
        elif isinstance(date_time, time):
            date_time = __now.replace(hour=date_time.hour, minute=date_time.minute, second=date_time.second)
            if date_time < __now:
                date_time += timedelta(days=1)
        assert isinstance(date_time, datetime), type(date_time)

        assert date_time >= __now, f'Time for callback must be in the future!\nTime: {date_time}\nNow : {__now}'

        self._callback = callback
        self._args = args
        self._kwargs = kwargs

        self.is_due = False
        self.is_finished = False

        self.next_call = date_time

    def get_next_call(self):
        "Return the next execution timestamp"
        return self.next_call

    def check_due(self, now : datetime):

        self.is_due = True if self.next_call <= now else False
        if not self.is_due:
            return False

        if self.is_finished:
            self.is_due = False
            return False

        self.is_finished = True
        return self.is_due

    def execute(self, workers : ThreadPoolExecutor):
        if not self.is_due:
            return False

        workers.submit(self._callback, *self._args, **self._kwargs)
        return True

    def cancel(self):
        self.is_due = False
        self.is_finished = True