import itertools
import logging
import traceback
import typing
from asyncio import iscoroutinefunction, run_coroutine_threadsafe, sleep
from types import FunctionType, MethodType
import logging.handlers

from HABApp.core.const import loop

_FUNCS: typing.List[typing.Callable[[], typing.Any]] = []
_FUNCS_LAST: typing.List[typing.Callable[[], typing.Any]] = []

requested: bool = False


def register_func(func, last=False):
    assert isinstance(func, (FunctionType, MethodType)) or iscoroutinefunction(func), print(type(func))
    if last:
        _FUNCS_LAST.append(func)
    else:
        _FUNCS.append(func)


def request_shutdown():
    run_coroutine_threadsafe(_shutdown(), loop)


async def _shutdown():
    global requested
    "Request execution of all functions"

    log = logging.getLogger('HABApp.Shutdown')
    log.debug('Requested shutdown')

    requested = True

    for func in itertools.chain(_FUNCS, _FUNCS_LAST):
        try:
            log.debug(f'Calling {func.__module__}.{func.__name__}')
            if iscoroutinefunction(func):
                await func()
            else:
                func()
            log.debug(f'{func.__name__} done!')
            await sleep(0.01)
        except Exception as ex:
            log.error(ex)
            tb = traceback.format_exc().splitlines()
            for line in tb:
                log.error(line)

    log.debug('Shutdown complete')
    return None
