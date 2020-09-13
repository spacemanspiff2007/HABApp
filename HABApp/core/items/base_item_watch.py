import asyncio
import typing

import HABApp
from ..const import loop
from HABApp.core.lib import PendingFuture
from ..events import ItemNoChangeEvent, ItemNoUpdateEvent


class BaseWatch:
    EVENT: typing.Union[typing.Type[ItemNoUpdateEvent], typing.Type[ItemNoChangeEvent]]

    def __init__(self, name: str, secs: typing.Union[int, float]):
        self._fut = PendingFuture(self._post_event, secs)
        self._name: str = name

    async def _post_event(self):
        HABApp.core.EventBus.post_event(self._name, self.EVENT(self._name, self._fut.secs))

    async def __cancel_watch(self):
        self._fut.cancel()

    def cancel(self):
        """Cancel the item watch"""
        asyncio.run_coroutine_threadsafe(self.__cancel_watch(), loop)


class ItemNoUpdateWatch(BaseWatch):
    EVENT = ItemNoUpdateEvent


class ItemNoChangeWatch(BaseWatch):
    EVENT = ItemNoChangeEvent
