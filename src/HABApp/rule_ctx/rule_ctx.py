import logging
from typing import Optional, Callable

import HABApp
from HABApp.core.const.topics import ALL_TOPICS
from HABApp.core.internals import Context, uses_item_registry, HINT_EVENT_BUS_LISTENER
from HABApp.core.internals import uses_event_bus
from HABApp.core.internals.event_bus import EventBusBaseListener

event_bus = uses_event_bus()
item_registry = uses_item_registry()

log = logging.getLogger('HABApp.Rule')


class HABAppRuleContext(Context):
    def __init__(self, rule: 'HABApp.rule.Rule'):
        super().__init__()
        self.rule: Optional['HABApp.rule.Rule'] = rule

    def get_callback_name(self, callback: Callable) -> Optional[str]:
        return f'{self.rule.rule_name}.{callback.__name__}' if self.rule.rule_name else None

    def add_event_listener(self, listener: HINT_EVENT_BUS_LISTENER) -> HINT_EVENT_BUS_LISTENER:
        event_bus.add_listener(listener)
        return listener

    def remove_event_listener(self, listener: HINT_EVENT_BUS_LISTENER) -> HINT_EVENT_BUS_LISTENER:
        event_bus.remove_listener(listener)
        return listener

    def unload_rule(self):
        with HABApp.core.wrapper.ExceptionToHABApp(log):
            rule = self.rule

            # Unload the scheduler
            rule.run._scheduler.cancel_all()
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
            rule.on_rule_removed()

    def check_rule(self):
        with HABApp.core.wrapper.ExceptionToHABApp(log):
            # We need items if we want to run the test
            if item_registry.get_items():

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
            self.rule.run._scheduler.resume()

            # user implementation
            self.rule.on_rule_loaded()
