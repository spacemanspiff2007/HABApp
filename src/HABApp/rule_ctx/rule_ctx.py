from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final, TypeVar

import HABApp
from HABApp.core.const.topics import ALL_TOPICS
from HABApp.core.internals import (
    Context,
    EventBus,
    EventBusListener,
    ExecutorFactory,
    ItemRegistry,
)
from HABApp.core.internals.event_bus import EventBusListenerBase
from HABApp.core.lib import get_obj_name


if TYPE_CHECKING:
    from collections.abc import Callable

    from HABApp import Rule


log = logging.getLogger('HABApp.Rule')


TB = TypeVar('TB', bound=EventBusListener)


class HABAppRuleContext(Context):
    def __init__(self, rule: Rule, event_bus: EventBus, item_registry: ItemRegistry, executor_factory: ExecutorFactory) -> None:
        super().__init__()
        self.rule: Final[Rule] = rule
        self.event_bus: Final = event_bus
        self.item_registry: Final = item_registry
        self.executor_factory: Final = executor_factory

    def get_callback_name(self, callback: Callable) -> str | None:
        return f'{self.rule.rule_name}.{get_obj_name(callback):s}' if self.rule.rule_name else None

    def add_event_listener(self, listener: TB) -> TB:
        self.event_bus.add_listener(listener)
        return listener

    def remove_event_listener(self, listener: TB) -> TB:
        self.event_bus.remove_listener(listener)
        return listener

    async def unload_rule(self) -> None:
        with HABApp.core.wrapper.ExceptionToHABApp(log):
            rule = self.rule

            # Unload the scheduler
            rule.run._scheduler.set_enabled(False)
            rule.run._scheduler.remove_all()
            rule.run._habapp_ctx = None

            # cancel things and set obj to None
            while self.objs:
                with HABApp.core.wrapper.ExceptionToHABApp(log):
                    to_cancel = next(iter(self.objs))
                    to_cancel.cancel()
            self.objs = None    # Set to None so we crash if we want to schedule new stuff

            # clean references
            rule._habapp_ctx = None

            # user implementation
            await self.executor_factory.create(rule.on_rule_removed).execute()

    async def check_rule(self) -> None:
        with HABApp.core.wrapper.ExceptionToHABApp(log):
            # We need items if we want to run the test
            if self.item_registry:

                # Check if we have a valid item for all listeners
                for listener in self.objs:
                    if not isinstance(listener, EventBusListenerBase):
                        continue

                    # Internal topics - don't warn there
                    if listener.topic in ALL_TOPICS:
                        continue

                    # check if specific item exists
                    if not self.item_registry.item_exists(listener.topic):
                        log.warning(f'Item "{listener.topic}" does not exist (yet)! '
                                    f'self.listen_event in "{self.rule.rule_name}" may not work as intended.')

            # enable the scheduler
            self.rule.run._scheduler.set_enabled(True)

            # user implementation
            await self.executor_factory.create(self.rule.on_rule_loaded).execute()
