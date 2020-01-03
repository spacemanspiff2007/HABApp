import functools
import logging
import traceback
import asyncio

import HABApp

log = logging.getLogger('HABApp')


def __process_exception(func, e: Exception, do_print=False):
    lines = traceback.format_exc().splitlines()
    del lines[1:3]  # Remove entries which point to this wrapper

    # log exception, since it is unexpected we push it to stdout, too
    if do_print:
        print(f'Error {e} in {func.__name__}:')
    log.error(f'Error {e} in {func.__name__}:')
    for line in lines:
        if do_print:
            print(line)
        log.error(line)

    # send Error to internal event bus so we can reprocess it and notify the user
    HABApp.core.EventBus.post_event(
        'HABApp.Errors', HABApp.core.events.habapp_events.HABAppError(
            func_name=func.__name__, exception=e, traceback='\n'.join(lines)
        )
    )


def log_exception(func):
    # return async wrapper
    if asyncio.iscoroutine(func) or asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def a(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                __process_exception(func, e, do_print=True)
                # re raise exception, since this is something we didn't anticipate
                raise

        return a

    @functools.wraps(func)
    def f(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            __process_exception(func, e, do_print=True)
            # re raise exception, since this is something we didn't anticipate
            raise

    return f


def ignore_exception(func):
    # return async wrapper
    if asyncio.iscoroutine(func) or asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def a(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                __process_exception(func, e)
                return None

        return a

    @functools.wraps(func)
    def f(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            __process_exception(func, e)
            return None
    return f
