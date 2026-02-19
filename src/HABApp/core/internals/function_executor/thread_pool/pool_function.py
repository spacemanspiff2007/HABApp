from __future__ import annotations

from time import monotonic
from typing import TYPE_CHECKING, Final

from HABApp.core.asyncio import loop_context, run_func_from_async
from HABApp.core.internals import Context, ContextProvidingObj


if TYPE_CHECKING:
    from asyncio import AbstractEventLoop
    from collections.abc import Callable

    from HABApp.core.internals.function_executor.callable_executor import CallablePoolExecutor
    from HABApp.core.internals.function_executor.thread_pool import HABAppThreadPool


class PoolFunction[**P, R](ContextProvidingObj):
    __slots__ = (
        '_loop',
        'dur_run',
        'dur_start',
        'executor',
        'func',
        'func_args',
        'func_kwargs',
        'pool',
        'submitted',
        'usage_high'
    )

    def __init__(self, executor: CallablePoolExecutor, pool: HABAppThreadPool, func: Callable[P, R], *, args: P.args,
                 context: Context | None = None, kwargs: P.kwargs, loop: AbstractEventLoop) -> None:
        super().__init__(context=context)

        self.executor: Final = executor
        self.pool: Final = pool
        self.func: Final = func
        self.func_args: Final = args
        self.func_kwargs: Final = kwargs

        # timing checks
        self.submitted: float = monotonic()
        self.dur_start: float = 0.0
        self.dur_run: float = 0.0

        # thread info
        self.usage_high: int = 0

        self._loop: Final = loop

    def run(self) -> R:
        loop_token: Final = loop_context.set(self._loop)

        try:
            ts_start = monotonic()
            self.dur_start = ts_start - self.submitted

            self.pool.func_start(self)

            # notify if we don't process quickly
            if self.dur_start > 0.05:
                self.executor.log.warning(
                    f'Starting of {self.executor.name} took too long: {self.dur_start:.2f}s. '
                    f'Maybe there are not enough threads?'
                )

            # Execute the function
            ret = self.func(*self.func_args, **self.func_kwargs)

            # log warning if execution takes too long
            self.dur_run = monotonic() - ts_start

            if self.executor.warn_too_long and self.dur_run > 0.8 and self.usage_high >= self.pool.max_workers * 0.6:
                self.executor.log.warning(
                    f'{self.usage_high:d}/{self.pool.max_workers:d} threads have been in use and '
                    f'execution of {self.executor.name} took too long: {self.dur_run:.2f}s'
                )

        except Exception as e:
            # Process and dump the exception traceback from a coroutine.
            # That way we effectively serialize the logged tracebacks in case two exceptions happen at once
            run_func_from_async(self.executor.process_exception, e, *self.func_args, **self.func_kwargs)
        else:
            return ret
        finally:
            loop_context.reset(loop_token)
            self.pool.func_complete(self)
