from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from HABApp.core.asyncio import run_func_from_async
from HABApp.core.events import EventFilter
from HABApp.core.internals import (
    AutoContextBoundObj,
    ContextBoundEventBusListener,
    EventBus,
    EventBusListener,
    get_current_context,
)
from HABApp.core.items.base_item_watch import DebouncedNoChangeEvent, DebouncedNoUpdateEvent
from HABApp.core.lib import DebouncedCallRegistry
from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.rule_ctx import HABAppRuleContext


if TYPE_CHECKING:
    from whenever import Instant

    from HABApp.core.const.hints import TYPE_EVENT_CALLBACK
    from HABApp.core.items.base_item_watch import DebouncedEventBase

log = logging.getLogger('HABApp')


class ItemTimeBase:
    __slots__ = ('_factories', 'instant')

    def __init__(self, instant: Instant) -> None:
        self.instant: Instant = instant
        self._factories: tuple[DebouncedEventBase, ...] = ()

    def set(self, instant: Instant, *, events: bool = True) -> None:
        self.instant = instant
        if not self._factories:
            return None

        if events:
            run_func_from_async(self._reset_factories)
        return None

    def _reset_factories(self) -> None:
        for event_factory in self._factories:
            event_factory.reset()

    def _get_event_factory(self) -> type[DebouncedEventBase]:
        raise NotImplementedError()

    def _get_factory(self, secs: float) -> DebouncedEventBase | None:
        for f in self._factories:
            if f.seconds == secs:
                return f
        return None

    def _add_watch(self, name: str, secs: float, context: HABAppRuleContext) -> ItemTimeWatch:
        secs = round(secs, 3)

        if (obj := self._get_factory(secs)) is None:
            obj = self._get_event_factory()(
                secs, name,
                registry=HABAPP_PROVIDER.get_existing(DebouncedCallRegistry),
                event_bus=HABAPP_PROVIDER.get_existing(EventBus),
            )
            self._factories = self._factories + (obj, )
            log.debug(f'Created {obj.log_desc():s}')

        obj.watcher_increase()

        # we need to explicitly pass the context because it gets lost by running this through run_func_from_async
        return ItemTimeWatch(self, obj, context=context)

    def _remove_watch(self, secs: float) -> None:
        secs = round(secs, 3)

        if (obj := self._get_factory(secs)) is None:
            return None

        if obj.watcher_decrease() > 0:
            return None

        self._factories = tuple(f for f in self._factories if f is not obj)
        log.debug(f'Removed {obj.log_desc():s}')
        obj.cancel()
        return None

    def add_watch(self, name: str, secs: float) -> ItemTimeWatch:
        return run_func_from_async(self._add_watch, name, secs, get_current_context())

    def remove_watch(self, secs: float) -> None:
        return run_func_from_async(self._remove_watch, secs)


class ItemUpdateTime(ItemTimeBase):
    def _get_event_factory(self) -> type[DebouncedEventBase]:
        return DebouncedNoUpdateEvent


class ItemChangeTime(ItemTimeBase):
    def _get_event_factory(self) -> type[DebouncedEventBase]:
        return DebouncedNoChangeEvent


class ItemTimeWatch(AutoContextBoundObj):
    def __init__(self, times: ItemTimeBase, event_factory: DebouncedEventBase,
                 context: HABAppRuleContext | None = None) -> None:
        super().__init__(parent_ctx=context)
        self._item_times: Final = times
        self._event_factory: Final = event_factory

    def cancel(self) -> None:
        """Cancel the item watch"""
        self._ctx_unlink()
        run_func_from_async(self._item_times.remove_watch, self._event_factory.seconds)

    def listen_event(self, callback: TYPE_EVENT_CALLBACK) -> EventBusListener:
        """Listen to (only) the event that is emitted by this watcher"""
        context: Final = get_current_context()
        factory: Final = self._event_factory
        return context.add_event_listener(
            ContextBoundEventBusListener(
                factory.item,
                context.executor_factory.create(callback, context=context),
                EventFilter(factory.event_cls(), seconds=factory.seconds),
                parent_ctx=context
            )
        )
