import logging
from asyncio import iscoroutinefunction
from collections.abc import Callable

from HABApp.config import CONFIG
from HABApp.core.internals import Context
from HABApp.core.internals.wrapped_function.base import TYPE_WRAPPED_FUNC_OBJ
from HABApp.core.internals.wrapped_function.wrapped_async import TYPE_FUNC_ASYNC, WrappedAsyncFunction
from HABApp.core.internals.wrapped_function.wrapped_sync import WrappedSyncFunction
from HABApp.core.internals.wrapped_function.wrapped_thread import (
    HINT_FUNC_SYNC,
    WrappedThreadFunction,
    create_thread_pool,
    run_in_thread_pool,
    stop_thread_pool,
)


def wrap_func(func: HINT_FUNC_SYNC | TYPE_FUNC_ASYNC,
              warn_too_long=True,
              name: str | None = None,
              logger: logging.Logger | None = None,
              context: Context | None = None) -> TYPE_WRAPPED_FUNC_OBJ:

    # Check that it's actually a callable, so we fail fast and not when we try to run the function.
    # Some users pass the result of the function call (e.g. func()) by accident
    # which will inevitably fail once we try to run the function.
    if not callable(func):
        try:
            type_name: str = func.__class__.__name__
        except Exception:
            type_name = type(func)

        msg = f'Callable or coroutine function expected! Got "{func}" (type {type_name:s})'
        raise TypeError(msg)

    if iscoroutinefunction(func):
        return WrappedAsyncFunction(func, name=name, logger=logger, context=context)

    return SYNC_CLS(func, warn_too_long=warn_too_long, name=name, logger=logger, context=context)


SYNC_CLS: type[WrappedThreadFunction] | type[WrappedSyncFunction]


def setup() -> None:
    global SYNC_CLS

    if not THREAD_POOL.enabled:
        SYNC_CLS = WrappedSyncFunction

        # In case of hot reload
        stop_thread_pool()
    else:
        SYNC_CLS = WrappedThreadFunction

        # create thread pool
        create_thread_pool(THREAD_POOL.threads)

        # this function can be called multiple times, so it's no problem if we register it more than once!
        from HABApp.runtime import shutdown
        shutdown.register_func(stop_thread_pool, msg='Stopping thread pool', last=True)


THREAD_POOL = CONFIG.habapp.thread_pool
THREAD_POOL.subscribe_for_changes(setup)


async def run_function(func: Callable):
    if not THREAD_POOL.enabled:
        return func()

    return await run_in_thread_pool(func)
