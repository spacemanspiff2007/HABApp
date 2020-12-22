import asyncio
import functools
import logging
import re
import sys
import typing
from logging import Logger
from pathlib import Path

import stackprinter

import HABApp

log = logging.getLogger('HABApp')


SUPPRESSED_PATHS = (
    re.compile(f'[/\\\\]{Path(__file__).name}$'),   # this file

    # rule file loader
    re.compile(r'[/\\]rule_file.py$'),
    re.compile(r'[/\\]runpy.py$'),

    # Worker functions
    re.compile(r'[/\\]wrappedfunction.py$'),

    # Don't print stack for used libraries
    re.compile(r'[/\\](site-packages|lib|python\d\.\d)[/\\]asyncio[/\\]'),
    re.compile(r'[/\\]site-packages[/\\]aiohttp[/\\]'),
    re.compile(r'[/\\]site-packages[/\\]voluptuous[/\\]'),
    re.compile(r'[/\\]site-packages[/\\]pydantic[/\\]'),
)

SKIP_TB = tuple(re.compile(k.pattern.replace('$', ', ')) for k in SUPPRESSED_PATHS)


def format_exception(e: typing.Union[Exception, typing.Tuple[typing.Any, typing.Any, typing.Any]]) -> typing.List[str]:
    tb = []
    skip = 0

    lines = stackprinter.format(e, line_wrap=0, truncate_vals=2000, suppressed_paths=SUPPRESSED_PATHS).splitlines()
    for i, line in enumerate(lines):
        if not skip:
            for s in SKIP_TB:
                if s.search(line):
                    # if it's just a two line traceback we skip it
                    if lines[i + 1].startswith('    ') and lines[i + 2].startswith('File'):
                        skip = 2
                        continue
        if skip:
            skip -= 1
            continue

        tb.append(line)

    return tb


def process_exception(func: typing.Union[typing.Callable, str], e: Exception,
                      do_print=False, logger: logging.Logger = log):
    # lines = traceback.format_exc().splitlines()
    # del lines[0:3]
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

    # send Error to internal event bus so we can reprocess it and notify the user
    HABApp.core.EventBus.post_event(
        HABApp.core.const.topics.ERRORS, HABApp.core.events.habapp_events.HABAppError(
            func_name=func_name, exception=e, traceback='\n'.join(lines)
        )
    )


def log_exception(func):
    # return async wrapper
    if asyncio.iscoroutinefunction(func) or asyncio.iscoroutine(func):
        @functools.wraps(func)
        async def a(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except asyncio.CancelledError:
                pass
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
            except asyncio.CancelledError:
                pass
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

        # tb = traceback.format_exception(exc_type, exc_val, exc_tb)
        # # there is an inconsistent use of newlines and array entries so we normalize it
        # tb = '\n'.join(map(lambda x: x.strip(' \n'), tb))
        # tb = tb.splitlines()

        tb = format_exception((exc_type, exc_val, exc_tb))

        # possibility to reprocess tb
        if self.proc_tb is not None:
            tb = self.proc_tb(tb)

        # try to get the parent function name
        try:
            f_name = sys._getframe().f_back.f_code.co_name
        except Exception:
            f_name = 'Exception while getting the function name!'

        # log error
        if self.log is not None:
            self.log.log(self.log_level, f'Error "{exc_val}" in {f_name}:')
            for line in tb:
                self.log.log(self.log_level, line)

        # send Error to internal event bus so we can reprocess it and notify the user
        HABApp.core.EventBus.post_event(
            HABApp.core.const.topics.WARNINGS if self.log_level == logging.WARNING else HABApp.core.const.topics.ERRORS,
            HABApp.core.events.habapp_events.HABAppError(
                func_name=f_name, exception=exc_val, traceback='\n'.join(tb)
            )
        )
        return self.ignore_exception
