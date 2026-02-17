from __future__ import annotations

import warnings
from asyncio import AbstractEventLoop
from collections.abc import Callable, Hashable, Iterable, Mapping
from typing import TYPE_CHECKING, Any, Final, Self, override

from eascheduler.builder import FilterBuilder, JobBuilder, TriggerBuilder
from eascheduler.builder.helper import HINT_INSTANT, HINT_TIMEDELTA, get_instant, get_pos_timedelta_secs
from eascheduler.builder.triggers import TriggerObject, _get_producer
from eascheduler.executor import ExecutorBase
from eascheduler.jobs import CountdownJob, DateTimeJob, OneTimeJob
from eascheduler.schedulers.async_scheduler import AsyncScheduler
from typing_extensions import ParamSpec

from HABApp.core.asyncio import run_func_from_async
from HABApp.core.internals import Context
from HABApp.core.internals.function_executor import ExecutorFactory, FunctionExecutorBase
from HABApp.rule.scheduler.job_ctrl import CountdownJobControl, DateTimeJobControl, OneTimeJobControl


if TYPE_CHECKING:

    from HABApp.rule_ctx import HABAppRuleContext


HINT_CB_P = ParamSpec('HINT_CB_P')
type HINT_CB[**HINT_CB_P] = Callable[HINT_CB_P, Any]


class WrappedHabappExecutor(ExecutorBase):
    def __init__(self, func: FunctionExecutorBase,
                 args: Iterable = (), kwargs: Mapping[str, Any] | None = None) -> None:
        self._func: Final = func
        self._args: Final = args
        self._kwargs: Final = kwargs if kwargs is not None else {}

    @override
    def execute(self) -> None:
        self._func.execute_background(*self._args, **self._kwargs)


def wrapped_habapp_executor(func: Any, args: Iterable = (), kwargs: Mapping[str, Any] | None = None) -> ExecutorBase:
    return WrappedHabappExecutor(func, args, kwargs)


class AsyncHABAppScheduler(AsyncScheduler):

    @override
    def set_enabled(self, enabled: bool) -> Self:
        return run_func_from_async(super().set_enabled, enabled)


class HABAppJobBuilder:
    def __init__(self, context: HABAppRuleContext, *, loop: AbstractEventLoop, executor: ExecutorFactory) -> None:
        self._habapp_rule_ctx: Context = context
        self._executor: Final = executor
        self._scheduler: Final = AsyncHABAppScheduler(event_loop=loop, enabled=False)

        self._builder: Final = JobBuilder(self._scheduler, wrapped_habapp_executor)

        self.trigger: Final = TriggerBuilder
        self.filter: Final = FilterBuilder

    def _create_countdown(self, secs: HINT_TIMEDELTA, callback: HINT_CB,
                          *args: HINT_CB_P.args,
                          job_id: Hashable | None = None, **kwargs: HINT_CB_P.kwargs) -> CountdownJobControl:

        callback = self._executor.create(callback, context=self._habapp_rule_ctx)

        job = CountdownJob(wrapped_habapp_executor(callback, args, kwargs), get_pos_timedelta_secs(secs), job_id=job_id)
        job.link_scheduler(self._scheduler)
        return CountdownJobControl(job)

    def countdown(self, secs: HINT_TIMEDELTA, callback: HINT_CB,
                  *args: HINT_CB_P.args,
                  job_id: Hashable | None = None, **kwargs: HINT_CB_P.kwargs) -> CountdownJobControl:
        """Create a job that count town a certain time and then execute.

        :param secs: countdown time in seconds
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param job_id:
        :param kwargs: |param_scheduled_cb_kwargs|
        :return: Created job
        """
        return run_func_from_async(self._create_countdown, secs, callback, *args, job_id=job_id, **kwargs)

    def _create_once(self, instant: HINT_INSTANT, callback: HINT_CB,
                     *args: HINT_CB_P.args,
                     job_id: Hashable | None = None, **kwargs: HINT_CB_P.kwargs) -> OneTimeJobControl:

        callback = self._executor.create(callback, context=self._habapp_rule_ctx)

        job = OneTimeJob(wrapped_habapp_executor(callback, args, kwargs), get_instant(instant), job_id=job_id)
        job.link_scheduler(self._scheduler)
        return OneTimeJobControl(job)

    def once(self, instant: HINT_INSTANT, callback: HINT_CB,
             *args: HINT_CB_P.args,
             job_id: Hashable | None = None, **kwargs: HINT_CB_P.kwargs) -> OneTimeJobControl:
        """Create a job that runs once.

        :param instant: countdown time in seconds
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param job_id:
        :param kwargs: |param_scheduled_cb_kwargs|
        :return: Created job
        """
        return run_func_from_async(self._create_once, instant, callback, *args, job_id=job_id, **kwargs)

    def _create_at(self, trigger: TriggerObject, callback: HINT_CB,
                   *args: HINT_CB_P.args,
                   job_id: Hashable | None = None, **kwargs: HINT_CB_P.kwargs) -> DateTimeJobControl:

        callback = self._executor.create(callback, context=self._habapp_rule_ctx)

        job = DateTimeJob(wrapped_habapp_executor(callback, args, kwargs), _get_producer(trigger), job_id=job_id)
        job.link_scheduler(self._scheduler)
        return DateTimeJobControl(job)

    def at(self, trigger: TriggerObject, callback: HINT_CB,
           *args: HINT_CB_P.args,
           job_id: Hashable | None = None, **kwargs: HINT_CB_P.kwargs) -> DateTimeJobControl:
        """Create a job that will run when a provided trigger occurs.

        :param trigger:
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param job_id:
        :param kwargs: |param_scheduled_cb_kwargs|
        :return: Created job
        """

        # at produces not reoccurring executions, try to make migration graceful
        if not isinstance(trigger, TriggerObject):
            warnings.warn(
                'self.run.at must be called with a Trigger. Use self.run.once to schedule a single execution',
                DeprecationWarning, stacklevel=2
            )
            return self.once(trigger, callback, *args, job_id=job_id, **kwargs)

        return run_func_from_async(self._create_at, trigger, callback, *args, job_id=job_id, **kwargs)

    # ------------------------------------------------------------------------------------------------------------------
    # convenience functions
    # ------------------------------------------------------------------------------------------------------------------
    def soon(self, callback: HINT_CB,
             *args: HINT_CB_P.args,
             job_id: Hashable | None = None, **kwargs: HINT_CB_P.kwargs) -> OneTimeJobControl:
        """
        Run the callback as soon as possible.

        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        return self.once(None, callback, *args, job_id=job_id, **kwargs)
