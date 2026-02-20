from __future__ import annotations

import asyncio
import logging.handlers
import signal
from typing import TYPE_CHECKING, Final

from HABApp.core.provider import HABAPP_PROVIDER


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from typing import Any


log = logging.getLogger('HABApp.Shutdown')


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

    # register shutdown helper
    log.debug('Registering shutdown signal handlers')
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    yield obj

    # restore default behavior
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
