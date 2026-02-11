from __future__ import annotations

import asyncio
import logging.handlers
import signal
import traceback
from asyncio import sleep
from dataclasses import dataclass
from inspect import iscoroutinefunction
from types import BuiltinMethodType, FunctionType, MethodType
from typing import TYPE_CHECKING, Final

from HABApp.core.asyncio import create_task
from HABApp.core.lib.helper import get_obj_name
from HABApp.core.provider import HABAPP_PROVIDER


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Awaitable, Callable
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
        msg = f'{func.__module__}.{get_obj_name(func)}'

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


class ShutdownInfo:
    def __init__(self) -> None:
        self._requested: bool = False
        self._event: Final[asyncio.Event] = asyncio.Event()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} requested={self._requested}>'

    async def wait_for_shutdown(self) -> None:
        await self._event.wait()

    async def sleep(self, delay: float) -> None:
        if self._event.is_set():
            # if we sleep in a loop we should have a small delay to allow other tasks to run
            await asyncio.sleep(0.05)
            return None

        try:  # noqa: SIM105
            await asyncio.wait_for(self._event.wait(), timeout=delay)
        except TimeoutError:
            pass

        return None

    def is_requested(self) -> bool:
        return self._requested

    def request_showdown(self) -> None:
        if not self._requested:
            self._requested = True
            self._event.set()


@HABAPP_PROVIDER.register
async def __shutdown_factory() -> AsyncGenerator[ShutdownInfo, Any]:

    loop: Final = asyncio.get_event_loop()
    obj: Final = ShutdownInfo()

    def shutdown_handler(sig: Any, frame: Any) -> None:
        print('Shutting down ...')
        log.debug('Requested shutdown')

        loop.call_soon_threadsafe(obj.request_showdown)
        request()

    # register shutdown helper
    log.debug('Registering shutdown signal handlers')
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    yield obj

    # restore default behavior
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
