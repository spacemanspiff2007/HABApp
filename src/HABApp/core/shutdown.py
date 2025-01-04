from __future__ import annotations

import logging
import logging.handlers
import signal
import traceback
from asyncio import iscoroutinefunction, sleep
from collections.abc import Awaitable
from dataclasses import dataclass
from types import BuiltinMethodType, FunctionType, MethodType
from typing import TYPE_CHECKING

from HABApp.core.asyncio import create_task
from HABApp.core.const import loop


if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any, NoReturn


log = logging.getLogger('HABApp.Shutdown')


@dataclass(frozen=True)
class ShutdownBase:
    msg: str
    last: bool

    async def run(self) -> NoReturn:
        raise NotImplementedError()


@dataclass(frozen=True)
class ShutdownFunction(ShutdownBase):
    func: Callable[[], Any]

    async def run(self) -> None:
        self.func()


@dataclass(frozen=True)
class ShutdownAwaitable(ShutdownBase):
    func: Callable[[], Awaitable[Any]]

    async def run(self) -> None:
        await self.func()


_REGISTERED: tuple[ShutdownFunction | ShutdownAwaitable, ...] = ()

_REQUESTED: bool = False


def register(func: Callable[[], Any | Awaitable[Any]], *, last: bool = False, msg: str = '') -> None:
    global _REGISTERED

    if last is not True and last is not False:
        raise ValueError()

    if not isinstance(msg, str):
        raise TypeError()

    if not msg:
        msg = f'{func.__module__}.{func.__name__}'

    for existing in _REGISTERED:
        if existing.func is func:
            # If it's the same thing we don't call it multiple times
            if existing.msg == msg and existing.last == last:
                return None

            log.warning(f'Function {func} is already registered with a different message!')
            log.warning(f'  - {existing.msg:s}')
            log.warning(f'  - {msg:s}')
            return None

    if iscoroutinefunction(func):
        _REGISTERED += (ShutdownAwaitable(func=func, last=last, msg=msg), )
    elif isinstance(func, (FunctionType, MethodType, BuiltinMethodType)):
        _REGISTERED += (ShutdownFunction(func=func, last=last, msg=msg), )
    else:
        raise TypeError()


async def _shutdown() -> None:
    global _REQUESTED

    if _REQUESTED:
        return None
    _REQUESTED = True

    log.debug('Requested shutdown')

    objs = (
        *(obj for obj in _REGISTERED if not obj.last),
        *(obj for obj in _REGISTERED if obj.last),
        # shutdown of the event loop has to be the last thing that is done
        # since stopping of the loop exits the program
        ShutdownFunction(func=loop.stop, msg='Stopping asyncio loop', last=True)
    )

    for obj in objs:
        try:
            log.debug(f'{obj.msg}')
            await obj.run()
            log.debug('-> done!')
            await sleep(0.02)
        except Exception as ex:  # noqa: PERF203
            log.error(ex)
            tb = traceback.format_exc().splitlines()
            for line in tb:
                log.error(line)

    log.debug('Shutdown complete')


def request() -> None:
    create_task(_shutdown())


def is_requested() -> bool:
    return _REQUESTED


def register_signal_handler() -> None:
    def shutdown_handler(sig, frame) -> None:
        print('Shutting down ...')
        request()

    # register shutdown helper
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
