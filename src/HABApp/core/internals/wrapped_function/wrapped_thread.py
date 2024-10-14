from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from time import monotonic
from typing import TYPE_CHECKING, Any, Final

from typing_extensions import override

from HABApp.core.const import loop
from HABApp.core.internals import Context, ContextProvidingObj
from HABApp.core.internals.wrapped_function.base import P, R, WrappedFunctionBase, default_logger


if TYPE_CHECKING:
    import logging
    from collections.abc import Callable


POOL: ThreadPoolExecutor | None = None
POOL_THREADS: int = 0


def create_thread_pool(count: int) -> None:
    global POOL, POOL_THREADS

    if not isinstance(count, int) or count <= 0:
        msg = 'Thread count must be a positive integer'
        raise ValueError(msg)

    default_logger.debug(f'Starting thread pool with {count:d} threads!')

    stop_thread_pool()
    POOL_THREADS = count
    POOL = ThreadPoolExecutor(count, 'HabAppWorker')


def stop_thread_pool() -> None:
    global POOL, POOL_THREADS

    if (pool := POOL) is None:
        return None

    POOL_THREADS = 0
    POOL = None

    pool.shutdown()
    default_logger.debug('Thread pool stopped!')


POOL_INFO: Final[set[PoolFunc]] = set()
POOL_LOCK: Final = Lock()


class PoolFunc(ContextProvidingObj):
    def __init__(self, parent: WrappedThreadFunction, func_obj: Callable[..., Any], func_args: tuple[Any, ...],
                 func_kwargs: dict[str, Any], context: Context | None = None, **kwargs: Any) -> None:
        super().__init__(context=context, **kwargs)
        self.parent: Final = parent
        self.func_obj: Final = func_obj
        self.func_args: Final = func_args
        self.func_kwargs: Final = func_kwargs

        # timing checks
        self.submitted: float = monotonic()
        self.dur_start: float = 0.0
        self.dur_run: float = 0.0

        # thread info
        self.usage_high: int = 0

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} high: {self.usage_high:d}/{POOL_THREADS:d}>'

    def run(self) -> Any:
        pool_lock: Final = POOL_LOCK
        pool_info: Final = POOL_INFO
        parent = self.parent

        try:
            ts_start = monotonic()
            self.dur_start = ts_start - self.submitted

            with pool_lock:
                pool_info.add(self)
                count = len(pool_info)
                for info in pool_info:
                    info.usage_high = max(count, info.usage_high)

            # notify if we don't process quickly
            if self.dur_start > 0.05:
                parent.log.warning(f'Starting of {parent.name} took too long: {self.dur_start:.2f}s. '
                                   f'Maybe there are not enough threads?')

            # Profiler does not work
            # https://github.com/python/cpython/issues/124656

            # Execute the function
            ret = self.func_obj(*self.func_args, **self.func_kwargs)

            # log warning if execution takes too long
            self.dur_run = monotonic() - ts_start

            if parent.warn_too_long and self.dur_run > 0.8 and self.usage_high >= POOL_THREADS * 0.6:
                parent.log.warning(f'{self.usage_high}/{POOL_THREADS} threads have been in use and '
                                   f'execution of {parent.name} took too long: {self.dur_run:.2f}s')

        except Exception as e:
            self.parent.process_exception(e, *self.func_args, **self.func_kwargs)
            return None
        else:
            return ret
        finally:
            with pool_lock:
                pool_info.discard(self)


class WrappedThreadFunction(WrappedFunctionBase[P, R]):

    def __init__(self, func: Callable[P, R],
                 warn_too_long: bool = True,
                 name: str | None = None,
                 logger: logging.Logger | None = None,
                 context: Context | None = None) -> None:

        super().__init__(name=name, func=func, logger=logger, context=context)

        self.func: Final = func
        self.warn_too_long: Final = warn_too_long

    @override
    def run(self, *args: P.args, **kwargs: P.kwargs) -> None:
        # we need to copy the context, so it's available when the function is run
        pool_func = PoolFunc(self, self.func, args, kwargs, context=self._habapp_ctx)
        POOL.submit(pool_func.run)
        return None

    @override
    async def async_run(self, *args: P.args, **kwargs: P.kwargs) -> R | None:

        pool_func = PoolFunc(self, self.func, args, kwargs, context=self._habapp_ctx)
        return await loop.run_in_executor(POOL, pool_func.run)
