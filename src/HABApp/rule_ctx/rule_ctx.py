from __future__ import annotations

import logging
from typing import TYPE_CHECKING, TypeVar

import HABApp
from HABApp.core.const.topics import ALL_TOPICS
from HABApp.core.internals import Context, EventBusListener, uses_event_bus, uses_item_registry, wrap_func
from HABApp.core.internals.event_bus import EventBusBaseListener
from HABApp.core.lib import get_obj_name


if TYPE_CHECKING:
    from collections.abc import Callable

    from HABApp import Rule


event_bus = uses_event_bus()
item_registry = uses_item_registry()

log = logging.getLogger('HABApp.Rule')


TB = TypeVar('TB', bound=EventBusListener)


class HABAppRuleContext(Context):
    def __init__(self, rule: Rule) -> None:
        super().__init__()
        self.rule: Rule | None = rule

    def get_callback_name(self, callback: Callable) -> str | None:
        return f'{self.rule.rule_name}.{get_obj_name(callback):s}' if self.rule.rule_name else None

    def add_event_listener(self, listener: TB) -> TB:
        event_bus.add_listener(listener)
        return listener

    def remove_event_listener(self, listener: TB) -> TB:
        event_bus.remove_listener(listener)
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
            self.rule = None
            rule._habapp_rule_ctx = None

            # user implementation
            await wrap_func(rule.on_rule_removed).async_run()

    async def check_rule(self) -> None:
        with HABApp.core.wrapper.ExceptionToHABApp(log):
            # We need items if we want to run the test
            if item_registry:

                # Check if we have a valid item for all listeners
                for listener in self.objs:
                    if not isinstance(listener, EventBusBaseListener):
                        continue

                    # Internal topics - don't warn there
                    if listener.topic in ALL_TOPICS:
                        continue

                    # check if specific item exists
                    if not item_registry.item_exists(listener.topic):
                        log.warning(f'Item "{listener.topic}" does not exist (yet)! '
                                    f'self.listen_event in "{self.rule.rule_name}" may not work as intended.')

            # enable the scheduler
            self.rule.run._scheduler.set_enabled(True)

            # user implementation
            await wrap_func(self.rule.on_rule_loaded).async_run()
