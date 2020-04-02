from datetime import datetime, timedelta

import astral.sun
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
        func = getattr(astral.sun, self._method)
        observer = HABApp.config.CONFIG.location.astral_observer

        dt = datetime.now().date()
        self._next_base: datetime = func(observer=observer, date=dt).replace(microsecond=0)
        self._update_run_time()

        if self._next_call < datetime.now(tz=utc):
            self._next_base: datetime = func(observer=observer, date=dt + timedelta(days=1)).replace(microsecond=0)
            self._update_run_time()
