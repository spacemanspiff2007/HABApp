from __future__ import annotations

import logging
import typing

from HABApp.core.asyncio import run_func_from_async
from HABApp.core.events import EventFilter, ItemNoChangeEvent, ItemNoUpdateEvent
from HABApp.core.internals import (
    AutoContextBoundObj,
    ContextBoundEventBusListener,
    get_current_context,
    uses_post_event,
    wrap_func,
)
from HABApp.core.lib import PendingFuture


if typing.TYPE_CHECKING:
    import HABApp
    from HABApp.core.const.hints import TYPE_EVENT_CALLBACK


log = logging.getLogger('HABApp')

post_event = uses_post_event()


class BaseWatch(AutoContextBoundObj):
    EVENT: type[ItemNoUpdateEvent | ItemNoChangeEvent]

    def __init__(self, name: str, secs: int | float) -> None:
        super().__init__()
        self.fut = PendingFuture(self._post_event, secs)
        self.name: str = name

    async def _post_event(self) -> None:
        post_event(self.name, self.EVENT(self.name, self.fut.secs))

    def __cancel_watch(self) -> None:
        self.fut.cancel()
        log.debug(f'Canceled {self.__class__.__name__} ({self.fut.secs}s) for {self.name}')

    def cancel(self) -> None:
        """Cancel the item watch"""
        self._ctx_unlink()
        run_func_from_async(self.__cancel_watch)

    def listen_event(self, callback: TYPE_EVENT_CALLBACK) -> HABApp.core.base.EventBusListener:
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
