from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, time


class ScheduledCallback:

    VALIDATE_CALLBACK_DATETIME = True
    CALL_ONCE = True

    def __init__(self, date_time, callback, *args, **kwargs):

        # next time the callback will be executed
        __now = datetime.now()

        if isinstance(date_time, time):
            date_time = __now.replace(hour=date_time.hour, minute=date_time.minute, second=date_time.second)
            if date_time < __now:
                date_time += timedelta(days=1)
        assert isinstance(date_time, datetime), type(date_time)

        if ScheduledCallback.VALIDATE_CALLBACK_DATETIME:
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
        if self.is_finished:
            self.is_due = False

        return self.is_due

    def execute(self, workers : ThreadPoolExecutor):
        if not self.is_due or self.is_finished:
            return False

        workers.submit(self._callback, *self._args, **self._kwargs)

        if self.__class__.CALL_ONCE:
            self.is_finished = True
        return True

    def cancel(self):
        self.is_finished = True
