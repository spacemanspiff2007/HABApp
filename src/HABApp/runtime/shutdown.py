import itertools
import logging
import logging.handlers
import traceback
import typing
import signal
from asyncio import iscoroutinefunction, sleep
from dataclasses import dataclass
from types import FunctionType, MethodType
from typing import Callable, Coroutine, Union

from HABApp.core.asyncio import async_context, create_task
from HABApp.core.const import loop


@dataclass(frozen=True)
class ShutdownInfo:
    func: Union[Callable[[], typing.Any], Coroutine]
    msg: str
    last: bool


_FUNCS: typing.List[ShutdownInfo] = []

requested: bool = False


def register_func(func, last=False, msg: str = ''):
    assert isinstance(func, (FunctionType, MethodType)) or iscoroutinefunction(func), print(type(func))
    assert last is True or last is False, last
    assert isinstance(msg, str)

    _FUNCS.append(ShutdownInfo(func, f'{func.__module__}.{func.__name__}' if not msg else msg, last))


def register_signal_handler():
    def shutdown_handler(sig, frame):
        print('Shutting down ...')
        request_shutdown()

    # register shutdown helper
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)


def request_shutdown():
    create_task(_shutdown())


async def _shutdown():
    global requested
    "Request execution of all functions"

    async_context.set('Shutdown')

    log = logging.getLogger('HABApp.Shutdown')
    log.debug('Requested shutdown')

    requested = True

    for obj in itertools.chain(filter(lambda x: not x.last, _FUNCS),
                               filter(lambda x: x.last, _FUNCS),
                               # shutdown of the event loop has to be the last thing that is done
                               # since stopping of the loop exits the program
                               [ShutdownInfo(loop.stop, 'Stopping asyncio loop', last=True)]):
        try:
            log.debug(f'{obj.msg}')
            if iscoroutinefunction(obj.func):
                await obj.func()
            else:
                obj.func()
            log.debug('-> done!')
            await sleep(0.02)
        except Exception as ex:
            log.error(ex)
            tb = traceback.format_exc().splitlines()
            for line in tb:
                log.error(line)

    log.debug('Shutdown complete')
    return None
