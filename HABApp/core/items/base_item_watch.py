import asyncio
import typing

import HABApp, logging
from ..const import loop
from HABApp.core.lib import PendingFuture
from ..events import ItemNoChangeEvent, ItemNoUpdateEvent


log = logging.getLogger('HABApp')


class BaseWatch:
    EVENT: typing.Union[typing.Type[ItemNoUpdateEvent], typing.Type[ItemNoChangeEvent]]

    def __init__(self, name: str, secs: typing.Union[int, float]):
        self.fut = PendingFuture(self._post_event, secs)
        self.name: str = name

    async def _post_event(self):
        HABApp.core.EventBus.post_event(self.name, self.EVENT(self.name, self.fut.secs))

    async def __cancel_watch(self):
        self.fut.cancel()
        log.debug(f'Canceled {self.__class__.__name__} ({self.fut.secs}s) for {self.name}')

    def cancel(self):
        """Cancel the item watch"""
        asyncio.run_coroutine_threadsafe(self.__cancel_watch(), loop)


class ItemNoUpdateWatch(BaseWatch):
    EVENT = ItemNoUpdateEvent


class ItemNoChangeWatch(BaseWatch):
    EVENT = ItemNoChangeEvent
