import asyncio
import logging
import typing

import HABApp
from HABApp.core.lib import PendingFuture
from ..const import loop
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

    def listen_event(self, callback: typing.Callable[[typing.Any], typing.Any]) -> 'HABApp.core.EventBusListener':
        """Listen to (only) the event that is emitted by this watcher"""
        rule = HABApp.rule.get_parent_rule()
        cb = HABApp.core.WrappedFunction(callback, name=rule._get_cb_name(callback))
        listener = HABApp.core.EventBusListener(
            self.name, cb, self.EVENT, 'seconds', self.fut.secs
        )
        return rule._add_event_listener(listener)


class ItemNoUpdateWatch(BaseWatch):
    EVENT = ItemNoUpdateEvent


class ItemNoChangeWatch(BaseWatch):
    EVENT = ItemNoChangeEvent
