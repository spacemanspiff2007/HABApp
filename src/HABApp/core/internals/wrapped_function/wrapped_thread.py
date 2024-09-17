from __future__ import annotations

import io
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from cProfile import Profile
from pstats import SortKey, Stats
from threading import Lock
from time import monotonic
from typing import TYPE_CHECKING, Any, Final

from typing_extensions import override

from HABApp.core.asyncio import async_context
from HABApp.core.const import loop
from HABApp.core.internals import Context, ContextProvidingObj
from HABApp.core.internals.wrapped_function.base import WrappedFunctionBase, default_logger


if TYPE_CHECKING:
    import logging


POOL: ThreadPoolExecutor | None = None
POOL_THREADS: int = 0
POOL_INFO: set[PoolFunc] = set()
POOL_LOCK = Lock()


def create_thread_pool(count: int):
    global POOL, POOL_THREADS
    assert isinstance(count, int) and count > 0

    default_logger.debug(f'Starting thread pool with {count:d} threads!')

    stop_thread_pool()
    POOL_THREADS = count
    POOL = ThreadPoolExecutor(count, 'HabAppWorker')


def stop_thread_pool():
    global POOL, POOL_THREADS

    if (pool := POOL) is None:
        return None

    POOL_THREADS = 0
    POOL = None

    pool.shutdown()
    default_logger.debug('Thread pool stopped!')


async def run_in_thread_pool(func: Callable):
    return await loop.run_in_executor(
        POOL, func
    )


HINT_FUNC_SYNC = Callable[..., Any]


class PoolFunc(ContextProvidingObj):
    def __init__(self, parent: WrappedThreadFunction, func_obj: HINT_FUNC_SYNC, func_args: tuple[Any, ...],
                 func_kwargs: dict[str, Any], context: Context | None = None, **kwargs):
        super().__init__(context=context, **kwargs)
        self.parent: Final = parent
        self.func_obj: Final = func_obj
        self.func_args: Final = func_args
        self.func_kwargs: Final = func_kwargs

        # timing checks
        self.submitted = monotonic()
        self.dur_start = 0.0
        self.dur_run = 0.0

        # thread info
        self.usage_high = 0

    def __repr__(self):
        return f'<{self.__class__.__name__} high: {self.usage_high:d}/{POOL_THREADS:d}>'

    def run(self):
        try:
            ts_start = monotonic()
            self.dur_start = ts_start - self.submitted

            with POOL_LOCK:
                POOL_INFO.add(self)
                count = len(POOL_INFO)
                for info in POOL_INFO:
                    info.usage_high = max(count, info.usage_high)

            parent = self.parent

            # notify if we don't process quickly
            if self.dur_start > 0.05:
                parent.log.warning(f'Starting of {parent.name} took too long: {self.dur_start:.2f}s. '
                                   f'Maybe there are not enough threads?')

            # start profiler
            pr = Profile()
            pr.enable()

            # Execute the function
            self.func_obj(*self.func_args, **self.func_kwargs)

            # disable profiler
            pr.disable()

            # log warning if execution takes too long
            self.dur_run = monotonic() - ts_start

            if parent.warn_too_long and self.dur_run > 0.8 and self.usage_high >= POOL_THREADS * 0.6:
                parent.log.warning(f'{self.usage_high}/{POOL_THREADS} threads have been in use and '
                                   f'execution of {parent.name} took too long: {self.dur_run:.2f}s')

                s = io.StringIO()
                ps = Stats(pr, stream=s).sort_stats(SortKey.CUMULATIVE)
                ps.print_stats(0.1)  # limit to output to 10% of the lines

                for line in s.getvalue().splitlines()[4:]:  # skip the amount of calls and "Ordered by:"
                    if line:
                        parent.log.warning(line)

        except Exception as e:
            self.parent.process_exception(e, *self.func_args, **self.func_kwargs)
            return None
        finally:
            with POOL_LOCK:
                POOL_INFO.discard(self)


class WrappedThreadFunction(WrappedFunctionBase):

    def __init__(self, func: HINT_FUNC_SYNC,
                 warn_too_long=True,
                 name: str | None = None,
                 logger: logging.Logger | None = None,
                 context: Context | None = None):

        super().__init__(name=name, func=func, logger=logger, context=context)
        assert callable(func)

        self.func = func
        self.warn_too_long: bool = warn_too_long

    @override
    def run(self, *args, **kwargs):
        # we need to copy the context, so it's available when the function is run
        pool_func = PoolFunc(self, self.func, args, kwargs, context=self._habapp_ctx)
        return POOL.submit(pool_func.run)

    @override
    async def async_run(self, *args, **kwargs):

        token = async_context.set('WrappedThreadFunction')

        pool_func = PoolFunc(self, self.func, args, kwargs, context=self._habapp_ctx)
        await loop.run_in_executor(POOL, pool_func.run)

        async_context.reset(token)
