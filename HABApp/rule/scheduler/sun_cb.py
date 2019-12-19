from datetime import timedelta, datetime

from pytz import utc

import HABApp
from . import TYPING_DATE_TIME
from .base import ScheduledCallbackBase


class SunScheduledCallback(ScheduledCallbackBase):

    def __init__(self, callback, *args, **kwargs):
        super().__init__(callback, *args, **kwargs)
        self._method: str = None

    def sun_trigger(self, trig):
        assert trig in ('sunrise', 'sunset', 'dusk', 'dawn'), trig
        self._method = trig

    def set_next_run_time(self, date_time: TYPING_DATE_TIME) -> 'ScheduledCallbackBase':
        raise NotImplementedError()

    def _calculate_next_call(self):
        func = getattr(HABApp.config.config.CONFIG.location.astral, self._method)

        dt = datetime.now().date()
        self._next_base: datetime = func(date=dt, local=False)
        if self._next_base < datetime.now(tz=utc):
            self._next_base: datetime = func(date=dt + timedelta(days=1), local=False)
