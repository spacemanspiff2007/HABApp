from __future__ import annotations

from time import monotonic
from typing import TYPE_CHECKING, Final

from HABApp.core.internals import Context, ContextProvidingObj


if TYPE_CHECKING:
    from collections.abc import Callable

    from HABApp.core.internals.function_executor.callable_executor import CallablePoolExecutor
    from HABApp.core.internals.function_executor.thread_pool import HABAppThreadPool


class PoolFunction[**P, R](ContextProvidingObj):
    __slots__ = (
        'dur_finish', 'dur_start', 'executor', 'func', 'func_args', 'func_kwargs', 'pool', 'submitted', 'usage_high'
    )

    def __init__(self, executor: CallablePoolExecutor, pool: HABAppThreadPool, func: Callable[P, R], *args: P.args,
                 context: Context | None = None,  kwargs: P.kwargs) -> None:
        super().__init__(context=context)

        self.executor: Final = executor
        self.pool: Final = pool
        self.func: Final = func
        self.func_args: Final = args
        self.func_kwargs: Final = kwargs

        # timing checks
        self.submitted: float = monotonic()
        self.dur_start: float = 0.0
        self.dur_finish: float = 0.0

        # thread info
        self.usage_high: int = 0

    def run(self) -> R:
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
            ret = self.func(*self.args, **self.kwargs)

            # log warning if execution takes too long
            self.dur_run = monotonic() - ts_start

            if parent.warn_too_long and self.dur_run > 0.8 and self.usage_high >= self.pool.max_workers * 0.6:
                parent.log.warning(f'{self.usage_high:d}/{self.pool.max_workers:d} threads have been in use and '
                                   f'execution of {parent.name} took too long: {self.dur_run:.2f}s')

        except Exception as e:
            ...
        else:
            return ret
        finally:
            self.pool.func_complete(self)
