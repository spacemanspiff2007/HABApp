import logging
import typing

import HABApp
from HABApp.core.asyncio import create_task
from HABApp.core.events import ItemNoChangeEvent, ItemNoUpdateEvent, EventFilter
from HABApp.core.lib import PendingFuture
from HABApp.core.const.hints import TYPE_EVENT_CALLBACK
from HABApp.core.internals import uses_post_event, get_current_context, AutoContextBoundObj

log = logging.getLogger('HABApp')

post_event = uses_post_event()


class BaseWatch(AutoContextBoundObj):
    EVENT: typing.Union[typing.Type[ItemNoUpdateEvent], typing.Type[ItemNoChangeEvent]]

    def __init__(self, name: str, secs: typing.Union[int, float]):
        super(BaseWatch, self).__init__()
        self.fut = PendingFuture(self._post_event, secs)
        self.name: str = name

    async def _post_event(self):
        post_event(self.name, self.EVENT(self.name, self.fut.secs))

    async def __cancel_watch(self):
        self._ctx_unlink()
        self.fut.cancel()
        log.debug(f'Canceled {self.__class__.__name__} ({self.fut.secs}s) for {self.name}')

    def cancel(self):
        """Cancel the item watch"""
        create_task(self.__cancel_watch())

    def listen_event(self, callback: TYPE_EVENT_CALLBACK) -> 'HABApp.core.base.TYPE_EVENT_BUS_LISTENER':
        """Listen to (only) the event that is emitted by this watcher"""
        context = get_current_context()
        cb = HABApp.core.internals.wrap_func(callback, context=context)
        listener = HABApp.core.internals.EventBusListener(self.name, cb, EventFilter(self.EVENT, seconds=self.fut.secs))
        return context.add_event_listener(listener)


class ItemNoUpdateWatch(BaseWatch):
    EVENT = ItemNoUpdateEvent


class ItemNoChangeWatch(BaseWatch):
    EVENT = ItemNoChangeEvent
