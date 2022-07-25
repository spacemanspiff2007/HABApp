import logging
from asyncio import iscoroutinefunction
from typing import Union, Optional, Callable, Type

from HABApp.config import CONFIG
from HABApp.core.internals import HINT_CONTEXT_OBJ
from HABApp.core.internals.wrapped_function.base import TYPE_WRAPPED_FUNC_OBJ
from HABApp.core.internals.wrapped_function.wrapped_async import WrappedAsyncFunction, HINT_FUNC_ASYNC
from HABApp.core.internals.wrapped_function.wrapped_sync import WrappedSyncFunction
from HABApp.core.internals.wrapped_function.wrapped_thread import HINT_FUNC_SYNC, WrappedThreadFunction, \
    create_thread_pool, stop_thread_pool, run_in_thread_pool


def wrap_func(func: Union[HINT_FUNC_SYNC, HINT_FUNC_ASYNC],
              warn_too_long=True,
              name: Optional[str] = None,
              logger: Optional[logging.Logger] = None,
              context: Optional[HINT_CONTEXT_OBJ] = None) -> TYPE_WRAPPED_FUNC_OBJ:

    if iscoroutinefunction(func):
        return WrappedAsyncFunction(func, name=name, logger=logger, context=context)
    else:
        return SYNC_CLS(func, warn_too_long=warn_too_long, name=name, logger=logger, context=context)


SYNC_CLS: Union[Type[WrappedThreadFunction], Type[WrappedSyncFunction]]


def setup():
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
    else:
        return await run_in_thread_pool(func)
