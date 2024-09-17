from __future__ import annotations

import random
import warnings
from collections.abc import Callable, Hashable, Iterable, Mapping
from typing import TYPE_CHECKING, Any, Final, TypeAlias

from eascheduler.builder import FilterBuilder, JobBuilder, TriggerBuilder
from eascheduler.executor import ExecutorBase
from eascheduler.schedulers.async_scheduler import AsyncScheduler
from typing_extensions import ParamSpec, override

from HABApp.core.asyncio import create_task_from_async
from HABApp.core.const import loop
from HABApp.core.internals import Context, wrap_func
from HABApp.core.internals.wrapped_function.wrapped_async import WrappedAsyncFunction


if TYPE_CHECKING:
    from eascheduler.builder.helper import HINT_INSTANT, HINT_TIMEDELTA
    from eascheduler.builder.triggers import TriggerObject
    from eascheduler.job_control import CountdownJobControl, DateTimeJobControl, OneTimeJobControl

    from HABApp.core.internals.wrapped_function.wrapped_thread import WrappedThreadFunction
    from HABApp.rule_ctx import HABAppRuleContext


HINT_CB_P = ParamSpec('HINT_CB_P')
HINT_CB: TypeAlias = Callable[HINT_CB_P, Any]


class WrappedSyncExecutor(ExecutorBase):
    def __init__(self, func: WrappedThreadFunction,
                 args: Iterable = (), kwargs: Mapping[str, Any] | None = None) -> None:
        self._func: Final = func
        self._args: Final = args
        self._kwargs: Final = kwargs if kwargs is not None else {}

    @override
    def execute(self) -> None:
        self._func.run(*self._args, **self._kwargs)


class WrappedAsyncExecutor(ExecutorBase):
    def __init__(self, func: WrappedAsyncFunction,
                 args: Iterable = (), kwargs: Mapping[str, Any] | None = None) -> None:
        self._func: Final = func
        self._args: Final = args
        self._kwargs: Final = kwargs if kwargs is not None else {}

    @override
    def execute(self) -> None:
        create_task_from_async(
            self._func.async_run(*self._args, **self._kwargs),
            name=self._func.name
        )


def wrapped_func_executor(func: Any, args: Iterable = (), kwargs: Mapping[str, Any] | None = None) -> ExecutorBase:
    if isinstance(func, WrappedAsyncFunction):
        return WrappedAsyncExecutor(func, args, kwargs)
    return WrappedSyncExecutor(func, args, kwargs)


class HABAppJobBuilder:
    def __init__(self, context: HABAppRuleContext):
        self._habapp_rule_ctx: Context = context
        self._scheduler: Final = AsyncScheduler(event_loop=loop)
        self._builder: Final = JobBuilder(self._scheduler, wrapped_func_executor)

        self.trigger: Final = TriggerBuilder
        self.filter: Final = FilterBuilder

    def countdown(self, secs: HINT_TIMEDELTA, callback: HINT_CB,
                  *args: HINT_CB_P.args,
                  job_id: Hashable | None = None, **kwargs: HINT_CB_P.kwargs) -> CountdownJobControl:
        callback = wrap_func(callback, context=self._habapp_rule_ctx)
        return self._builder.countdown(secs, callback, *args, job_id=job_id, **kwargs)

    def once(self, instant: HINT_INSTANT, callback: HINT_CB,
             *args: HINT_CB_P.args,
             job_id: Hashable | None = None, **kwargs: HINT_CB_P.kwargs) -> OneTimeJobControl:
        callback = wrap_func(callback, context=self._habapp_rule_ctx)
        return self._builder.once(instant, callback, *args, job_id=job_id, **kwargs)

    def soon(self, callback: HINT_CB,
             *args: HINT_CB_P.args,
             job_id: Hashable | None = None, **kwargs: HINT_CB_P.kwargs) -> OneTimeJobControl:
        """
        Run the callback as soon as possible.

        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        callback = wrap_func(callback, context=self._habapp_rule_ctx)
        return self._builder.once(None, callback, *args, job_id=job_id, **kwargs)

    def at(self, trigger: TriggerObject, callback: HINT_CB,
           *args: HINT_CB_P.args,
           job_id: Hashable | None = None, **kwargs: HINT_CB_P.kwargs) -> DateTimeJobControl:
        callback = wrap_func(callback, context=self._habapp_rule_ctx)
        return self._builder.at(trigger, callback, *args, job_id=job_id, **kwargs)

    # ------------------------------------------------------------------------------------------------------------------
    # deprecated functions
    # ------------------------------------------------------------------------------------------------------------------
    def every(self, start_time, interval,
              callback: HINT_CB, *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> DateTimeJobControl:

        warnings.warn(
            'self.run.every is deprecated. Use self.run.at in combination with a trigger',
            DeprecationWarning
        )

        return self.at(
            TriggerBuilder.interval(start_time, interval),
            callback, *args, **kwargs
        )

    def on_day_of_week(self, time, weekdays,
                       callback: HINT_CB, *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> DateTimeJobControl:
        warnings.warn(
            'self.run.on_day_of_week is deprecated. Use self.run.at in combination with a trigger and a filter',
            DeprecationWarning
        )
        return self.at(
            TriggerBuilder.time(time).only_at(FilterBuilder.weekdays(weekdays)),
            callback, *args, **kwargs
        )

    def on_every_day(self, time, callback: HINT_CB,
                     *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> DateTimeJobControl:
        warnings.warn(
            'self.run.on_every_day is deprecated. Use self.run.at in combination with a trigger',
            DeprecationWarning
        )
        return self.at(
            TriggerBuilder.time(time),
            callback, *args, **kwargs
        )

    def on_sunrise(self, callback: HINT_CB,
                   *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> DateTimeJobControl:
        warnings.warn(
            'self.run.on_sunrise is deprecated. Use self.run.at in combination with a trigger', DeprecationWarning)
        return self.at(TriggerBuilder.sunrise(), callback, *args, **kwargs)

    def on_sunset(self, callback: HINT_CB,
                  *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> DateTimeJobControl:
        warnings.warn(
            'self.run.on_sunset is deprecated. Use self.run.at in combination with a trigger', DeprecationWarning)
        return self.at(TriggerBuilder.sunset(), callback, *args, **kwargs)

    def on_sun_dawn(self, callback: HINT_CB,
                  *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> DateTimeJobControl:
        warnings.warn(
            'self.run.on_sun_dawn is deprecated. Use self.run.at in combination with a trigger', DeprecationWarning)
        return self.at(TriggerBuilder.dawn(), callback, *args, **kwargs)

    def on_sun_dusk(self, callback: HINT_CB,
                    *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> DateTimeJobControl:
        warnings.warn(
            'self.run.on_sun_dusk is deprecated. Use self.run.at in combination with a trigger', DeprecationWarning)
        return self.at(TriggerBuilder.dusk(), callback, *args, **kwargs)

    def every_minute(self, callback: HINT_CB,
                     *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> DateTimeJobControl:
        warnings.warn(
            'self.run.every_minute is deprecated. Use self.run.at in combination with a trigger', DeprecationWarning)
        return self.at(TriggerBuilder.interval(random.randint(0, 60 - 1), 60), callback, *args, **kwargs)

    def every_hour(self, callback: HINT_CB,
                   *args: HINT_CB_P.args, **kwargs: HINT_CB_P.kwargs) -> DateTimeJobControl:
        warnings.warn(
            'self.run.every_hour is deprecated. Use self.run.at in combination with a trigger', DeprecationWarning)
        return self.at(TriggerBuilder.interval(random.randint(0, 3600 - 1), 3600), callback, *args, **kwargs)
