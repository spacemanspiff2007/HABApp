import random
from datetime import datetime as dt_datetime, time as dt_time, timedelta as dt_timedelta
from typing import Iterable, Union

from eascheduler import SchedulerView
from eascheduler.jobs import CountdownJob, DawnJob, DayOfWeekJob, DuskJob, OneTimeJob, ReoccurringJob, SunriseJob, \
    SunsetJob

import HABApp
import HABApp.rule_ctx
from HABApp.core import WrappedFunction
from HABApp.rule.scheduler.executor import WrappedFunctionExecutor
from HABApp.rule.scheduler.scheduler import HABAppScheduler as _HABAppScheduler


class HABAppSchedulerView(SchedulerView):
    def __init__(self, rule: 'HABApp.rule_ctx.HABAppRuleContext'):
        super().__init__(_HABAppScheduler(), WrappedFunctionExecutor)
        self._habapp_rule_ctx: 'HABApp.rule_ctx.HABAppRuleContext' = rule

    def at(self, time: Union[None, dt_datetime, dt_timedelta, dt_time, int], callback, *args, **kwargs) -> OneTimeJob:
        callback = WrappedFunction(callback, name=self._habapp_rule_ctx.get_callback_name(callback))
        return super().at(time, callback, *args, **kwargs)

    def countdown(self, expire_time: Union[dt_timedelta, float, int], callback, *args, **kwargs) -> CountdownJob:
        callback = WrappedFunction(callback, name=self._habapp_rule_ctx.get_callback_name(callback))
        return super().countdown(expire_time, callback, *args, **kwargs)

    def every(self, start_time: Union[None, dt_datetime, dt_timedelta, dt_time, int],
              interval: Union[int, float, dt_timedelta], callback, *args, **kwargs) -> ReoccurringJob:
        callback = WrappedFunction(callback, name=self._habapp_rule_ctx.get_callback_name(callback))
        return super().every(start_time, interval, callback, *args, **kwargs)

    def on_day_of_week(self, time: Union[dt_time, dt_datetime], weekdays: Union[str, Iterable[Union[str, int]]],
                       callback, *args, **kwargs) -> DayOfWeekJob:
        callback = WrappedFunction(callback, name=self._habapp_rule_ctx.get_callback_name(callback))
        return super().on_day_of_week(time, weekdays, callback, *args, **kwargs)

    def on_every_day(self, time: Union[dt_time, dt_datetime], callback, *args, **kwargs) -> DayOfWeekJob:
        """Create a job that will run at a certain time of day

        :param time: Time when the job will run
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        callback = WrappedFunction(callback, name=self._habapp_rule_ctx.get_callback_name(callback))
        return super().on_day_of_week(time, 'all', callback, *args, **kwargs)

    def on_sunrise(self, callback, *args, **kwargs) -> SunriseJob:
        callback = WrappedFunction(callback, name=self._habapp_rule_ctx.get_callback_name(callback))
        return super().on_sunrise(callback, *args, **kwargs)

    def on_sunset(self, callback, *args, **kwargs) -> SunsetJob:
        callback = WrappedFunction(callback, name=self._habapp_rule_ctx.get_callback_name(callback))
        return super().on_sunset(callback, *args, **kwargs)

    def on_sun_dawn(self, callback, *args, **kwargs) -> DawnJob:
        callback = WrappedFunction(callback, name=self._habapp_rule_ctx.get_callback_name(callback))
        return super().on_sun_dawn(callback, *args, **kwargs)

    def on_sun_dusk(self, callback, *args, **kwargs) -> DuskJob:
        callback = WrappedFunction(callback, name=self._habapp_rule_ctx.get_callback_name(callback))
        return super().on_sun_dusk(callback, *args, **kwargs)

    def soon(self, callback, *args, **kwargs) -> OneTimeJob:
        """
        Run the callback as soon as possible.

        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        return self.at(None, callback, *args, **kwargs)

    def every_minute(self, callback, *args, **kwargs) -> ReoccurringJob:
        """Picks a random second and runs the callback every minute

        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        start = dt_timedelta(seconds=random.randint(0, 60 - 1))
        interval = dt_timedelta(seconds=60)
        return self.every(start, interval, callback, *args, **kwargs)

    def every_hour(self, callback, *args, **kwargs) -> ReoccurringJob:
        """Picks a random minute and second and run the callback every hour

        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        start = dt_timedelta(seconds=random.randint(0, 3600 - 1))
        interval = dt_timedelta(hours=1)
        return self.every(start, interval, callback, *args, **kwargs)
