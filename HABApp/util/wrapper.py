import functools
import logging
import traceback
import asyncio
import sys

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


class ExceptionToHABApp:
    def __init__(self, logger=None, ignore_exception=True):
        self.log = logger
        self.ignore_exception = ignore_exception

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        tb = traceback.format_exc()

        # try to get the parent function name
        try:
            f_name = sys._getframe().f_back.f_code.co_name
        except Exception:
            f_name = 'Exception while getting the function name!'

        # log error
        if self.log is not None:
            self.log.error(f'Error {exc_val} in {f_name}:')
            for l in tb.splitlines():
                self.log.error(l)

        # send Error to internal event bus so we can reprocess it and notify the user
        HABApp.core.EventBus.post_event(
            'HABApp.Errors', HABApp.core.events.habapp_events.HABAppError(
                func_name=f_name, exception=exc_val, traceback=tb
            )
        )
        return self.ignore_exception
