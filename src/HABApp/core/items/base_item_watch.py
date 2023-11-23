import logging
import typing

import HABApp
from HABApp.core.asyncio import run_func_from_async
from HABApp.core.const.hints import TYPE_EVENT_CALLBACK
from HABApp.core.events import EventFilter, ItemNoChangeEvent, ItemNoUpdateEvent
from HABApp.core.internals import (
    AutoContextBoundObj,
    ContextBoundEventBusListener,
    get_current_context,
    uses_post_event,
    wrap_func,
)
from HABApp.core.lib import PendingFuture


log = logging.getLogger('HABApp')

post_event = uses_post_event()


class BaseWatch(AutoContextBoundObj):
    EVENT: typing.Union[typing.Type[ItemNoUpdateEvent], typing.Type[ItemNoChangeEvent]]

    def __init__(self, name: str, secs: typing.Union[int, float]):
        super().__init__()
        self.fut = PendingFuture(self._post_event, secs)
        self.name: str = name

    async def _post_event(self):
        post_event(self.name, self.EVENT(self.name, self.fut.secs))

    def __cancel_watch(self):
        self.fut.cancel()
        log.debug(f'Canceled {self.__class__.__name__} ({self.fut.secs}s) for {self.name}')

    def cancel(self):
        """Cancel the item watch"""
        self._ctx_unlink()
        run_func_from_async(self.__cancel_watch)

    def listen_event(self, callback: TYPE_EVENT_CALLBACK) -> 'HABApp.core.base.HINT_EVENT_BUS_LISTENER':
        """Listen to (only) the event that is emitted by this watcher"""
        context = get_current_context()
        return context.add_event_listener(
            ContextBoundEventBusListener(
                self.name,
                wrap_func(callback, context=context),
                EventFilter(self.EVENT, seconds=self.fut.secs),
                parent_ctx=context
            )
        )


class ItemNoUpdateWatch(BaseWatch):
    EVENT = ItemNoUpdateEvent


class ItemNoChangeWatch(BaseWatch):
    EVENT = ItemNoChangeEvent
