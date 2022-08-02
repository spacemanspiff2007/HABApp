import random
from datetime import datetime as dt_datetime, time as dt_time, timedelta as dt_timedelta
from typing import Iterable, Union, Callable, Any

import HABApp.rule_ctx
from HABApp.core.const.const import PYTHON_310
from HABApp.core.internals import ContextProvidingObj, HINT_CONTEXT_OBJ
from HABApp.core.internals import wrap_func
from HABApp.rule.scheduler.executor import WrappedFunctionExecutor
from HABApp.rule.scheduler.scheduler import HABAppScheduler as _HABAppScheduler
from eascheduler import SchedulerView
from eascheduler.jobs import CountdownJob, DawnJob, DayOfWeekJob, DuskJob, OneTimeJob, ReoccurringJob, SunriseJob, \
    SunsetJob

if PYTHON_310:
    from typing import TypeAlias, ParamSpec
else:
    from typing_extensions import TypeAlias, ParamSpec


HINT_CB_P = ParamSpec('HINT_CB_P')
HINT_CB: TypeAlias = Callable[HINT_CB_P, Any]


class HABAppSchedulerView(SchedulerView, ContextProvidingObj):
    def __init__(self, context: 'HABApp.rule_ctx.HABAppRuleContext'):
        super().__init__(_HABAppScheduler(), WrappedFunctionExecutor)
        self._habapp_rule_ctx: HINT_CONTEXT_OBJ = context

    def at(self, time: Union[None, dt_datetime, dt_timedelta, dt_time, int],
           callback: HINT_CB, *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> OneTimeJob:
        callback = wrap_func(callback, context=self._habapp_rule_ctx)
        return super().at(time, callback, *args, **kwargs)

    def countdown(self, expire_time: Union[dt_timedelta, float, int],
                  callback: HINT_CB, *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> CountdownJob:
        callback = wrap_func(callback, context=self._habapp_rule_ctx)
        return super().countdown(expire_time, callback, *args, **kwargs)

    def every(self, start_time: Union[None, dt_datetime, dt_timedelta, dt_time, int],
              interval: Union[int, float, dt_timedelta],
              callback: HINT_CB, *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> ReoccurringJob:
        callback = wrap_func(callback, context=self._habapp_rule_ctx)
        return super().every(start_time, interval, callback, *args, **kwargs)

    def on_day_of_week(self, time: Union[dt_time, dt_datetime], weekdays: Union[str, Iterable[Union[str, int]]],
                       callback: HINT_CB, *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> DayOfWeekJob:
        callback = wrap_func(callback, context=self._habapp_rule_ctx)
        return super().on_day_of_week(time, weekdays, callback, *args, **kwargs)

    def on_every_day(self, time: Union[dt_time, dt_datetime],
                     callback: HINT_CB, *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> DayOfWeekJob:
        """Create a job that will run at a certain time of day

        :param time: Time when the job will run
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        callback = wrap_func(callback, context=self._habapp_rule_ctx)
        return super().on_day_of_week(time, 'all', callback, *args, **kwargs)

    def on_sunrise(self, callback: HINT_CB, *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> SunriseJob:
        callback = wrap_func(callback, context=self._habapp_rule_ctx)
        return super().on_sunrise(callback, *args, **kwargs)

    def on_sunset(self, callback: HINT_CB, *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> SunsetJob:
        callback = wrap_func(callback, context=self._habapp_rule_ctx)
        return super().on_sunset(callback, *args, **kwargs)

    def on_sun_dawn(self, callback: HINT_CB, *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> DawnJob:
        callback = wrap_func(callback, context=self._habapp_rule_ctx)
        return super().on_sun_dawn(callback, *args, **kwargs)

    def on_sun_dusk(self, callback: HINT_CB, *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> DuskJob:
        callback = wrap_func(callback, context=self._habapp_rule_ctx)
        return super().on_sun_dusk(callback, *args, **kwargs)

    def soon(self, callback: HINT_CB, *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> OneTimeJob:
        """
        Run the callback as soon as possible.

        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        return self.at(None, callback, *args, **kwargs)

    def every_minute(self, callback: HINT_CB, *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> ReoccurringJob:
        """Picks a random second and runs the callback every minute

        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        start = dt_timedelta(seconds=random.randint(0, 60 - 1))
        interval = dt_timedelta(seconds=60)
        return self.every(start, interval, callback, *args, **kwargs)

    def every_hour(self, callback: HINT_CB, *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> ReoccurringJob:
        """Picks a random minute and second and run the callback every hour

        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        start = dt_timedelta(seconds=random.randint(0, 3600 - 1))
        interval = dt_timedelta(hours=1)
        return self.every(start, interval, callback, *args, **kwargs)
