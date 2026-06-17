from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import aiohttp

from HABApp.core.connections import BaseConnection


if TYPE_CHECKING:
    from HABApp.core.lib import InstantView, WatchedSingleConsumerQueue
    from HABApp.core.lib.asyncio import AsyncioProvider
    from HABApp.openhab.definitions.websockets.base import BaseOutEvent
    from HABApp.openhab.items import OpenhabItem, Thing


@dataclass
class OpenhabContext:
    version: tuple[int, int, int]
    is_oh41: bool

    # true when we waited during connect
    waited_for_openhab: bool

    created_items: dict[str, tuple[OpenhabItem, InstantView]]
    created_things: dict[str, tuple[Thing, InstantView]]

    @classmethod
    def new_context(cls, *, version: tuple[int, int, int]) -> OpenhabContext:

        return cls(
            version=version, is_oh41=version >= (4, 1),
            waited_for_openhab=False,
            created_items={}, created_things={},
        )


type CONTEXT_TYPE = OpenhabContext | None

type OhWebsocketQueue = WatchedSingleConsumerQueue[BaseOutEvent]
type OhHttpQueue = WatchedSingleConsumerQueue[tuple[str, str, bool]]


class OpenhabConnection(BaseConnection):
    def __init__(self, asyncio_provider: AsyncioProvider) -> None:
        super().__init__('openhab', asyncio_provider=asyncio_provider)
        self.context: CONTEXT_TYPE = None

    def is_silent_exception(self, e: Exception) -> bool:
        return isinstance(e, (
            # https://docs.aiohttp.org/en/stable/client_reference.html#client-exceptions
            aiohttp.ClientError,

            # aiohttp_sse_client Exceptions
            ConnectionRefusedError, ConnectionError, ConnectionAbortedError)
        )
