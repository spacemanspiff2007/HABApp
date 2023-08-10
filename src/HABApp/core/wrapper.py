import asyncio
import functools
import logging
import typing
from logging import Logger
# noinspection PyProtectedMember
from sys import _getframe as sys_get_frame
from typing import Union, Callable

from HABApp.core.const.topics import TOPIC_ERRORS as TOPIC_ERRORS
from HABApp.core.const.topics import TOPIC_WARNINGS as TOPIC_WARNINGS
from HABApp.core.events.habapp_events import HABAppException
from HABApp.core.internals import uses_post_event
from HABApp.core.lib import format_exception

log = logging.getLogger('HABApp')

post_event = uses_post_event()


def process_exception(func: Union[Callable, str], e: Exception,
                      do_print=False, logger: logging.Logger = log):
    lines = format_exception(e)

    func_name = func if isinstance(func, str) else func.__name__

    # log exception, since it is unexpected we push it to stdout, too
    if do_print:
        print(f'Error {e} in {func_name}:')
    logger.error(f'Error {e} in {func_name}:')
    for line in lines:
        if do_print:
            print(line)
        logger.error(line)

    # send Error to internal event bus, so we can reprocess it and notify the user
    post_event(TOPIC_ERRORS, HABAppException(func_name=func_name, exception=e, traceback='\n'.join(lines)))


def log_exception(func):
    # return async wrapper
    if asyncio.iscoroutinefunction(func) or asyncio.iscoroutine(func):
        @functools.wraps(func)
        async def a(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                process_exception(func, e, do_print=True)
                # re raise exception, since this is something we didn't anticipate
                raise

        return a

    @functools.wraps(func)
    def f(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            process_exception(func, e, do_print=True)
            # re raise exception, since this is something we didn't anticipate
            raise

    return f


def ignore_exception(func):
    # return async wrapper
    if asyncio.iscoroutinefunction(func) or asyncio.iscoroutine(func):
        @functools.wraps(func)
        async def a(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                process_exception(func, e)
                return None

        return a

    @functools.wraps(func)
    def f(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            process_exception(func, e)
            return None
    return f


class ExceptionToHABApp:
    def __init__(self, logger: typing.Optional[Logger] = None, log_level: int = logging.ERROR,
                 ignore_exception: bool = True):
        self.log: typing.Optional[Logger] = logger
        self.log_level = log_level
        self.ignore_exception: bool = ignore_exception

        self.raised_exception = False

        self.proc_tb: typing.Optional[typing.Callable[[list], list]] = None

    def __enter__(self):
        self.raised_exception = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        # no exception -> we exit gracefully
        if exc_type is None and exc_val is None:
            return True

        self.raised_exception = True

        tb = format_exception((exc_type, exc_val, exc_tb))

        # possibility to reprocess tb
        if self.proc_tb is not None:
            tb = self.proc_tb(tb)

        # try to get the parent function name
        try:
            f_name = sys_get_frame().f_back.f_code.co_name
        except Exception:
            f_name = 'Exception while getting the function name!'

        # log error
        if self.log is not None:
            self.log.log(self.log_level, f'Error "{exc_val}" in {f_name}:')
            for line in tb:
                self.log.log(self.log_level, line)

        # send Error to internal event bus so we can reprocess it and notify the user
        post_event(
            TOPIC_WARNINGS if self.log_level == logging.WARNING else TOPIC_ERRORS,
            HABAppException(func_name=f_name, exception=exc_val, traceback='\n'.join(tb))
        )
        return self.ignore_exception
