import logging
from typing import Set, Optional

import HABApp
from HABApp.core.internals import Context
from HABApp.core.internals import uses_event_bus

event_bus = uses_event_bus()

log = logging.getLogger('HABApp.Rule')


class HABAppRuleContext(Context):
    def __init__(self, rule: 'HABApp.rule.Rule'):
        super().__init__()

        self.rule: 'HABApp.rule.Rule' = rule

        self.event_listeners: Set['HABApp.core.base.TYPE_EVENT_BUS_LISTENER'] = set()

    def add_event_listener(self, obj: 'HABApp.core.event_bus_listener.EventBusListenerBase')\
            -> 'HABApp.core.event_bus_listener.EventBusListenerBase':
        """Add the EventBusListener to the registry and set the RuleContext"""
        assert obj not in self.event_listeners
        self.event_listeners.add(obj)
        self.set_rule_context(obj)
        event_bus.add_listener(obj)
        return obj

    def remove_event_listener(self, obj: 'HABApp.core.event_bus_listener.EventBusListenerBase'):
        self.event_listners.remove(obj)

    def get_callback_name(self, callback: callable) -> Optional[str]:
        return f'{self.rule.rule_name}.{callback.__name__}' if self.rule.rule_name else None

    def unload_rule(self):
        with HABApp.core.wrapper.ExceptionToHABApp(log):
            rule = self.rule

            # Unload the scheduler
            rule.run._scheduler.cancel_all()
            rule.run._habapp_rule_ctx = None

            # cancel things and set obj to None
            for name in ('event_listeners', 'cancel_objects'):
                obj = getattr(self, name)
                while obj:
                    with HABApp.core.wrapper.ExceptionToHABApp(log):
                        to_cancel = next(iter(obj))
                        to_cancel.cancel()
                setattr(self, name, None)   # Set to None so we crash if we want to schedule new stuff

            # clean references
            self.rule = None
            rule._habapp_rule_ctx = None

            # user implementation
            rule.on_rule_removed()

    def check_rule(self):
        with HABApp.core.wrapper.ExceptionToHABApp(log):
            # We need items if we want to run the test
            if HABApp.core.Items.get_items():

                # Check if we have a valid item for all listeners
                for listener in self.event_listeners:

                    # Internal topics - don't warn there
                    if listener.topic in HABApp.core.const.topics.ALL:
                        continue

                    # check if specific item exists
                    if not HABApp.core.Items.item_exists(listener.topic):
                        log.warning(f'Item "{listener.topic}" does not exist (yet)! '
                                    f'self.listen_event in "{self.rule.rule_name}" may not work as intended.')

            # enable the scheduler
            self.rule.run._scheduler.resume()

            # user implementation
            self.rule.on_rule_loaded()
