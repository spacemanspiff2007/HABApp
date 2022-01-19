from typing import Optional

import HABApp


class EventBusListenerBase:
    def __init__(self, topic: str):
        assert isinstance(topic, str), type(topic)
        self.topic: str = topic

        # Optional rule context if the listener was created in a Rule
        self._habapp_rule_ctx: Optional['HABApp.rule_ctx.HABAppRuleContext'] = None

    def notify_listeners(self, event):
        raise NotImplementedError()

    def describe(self):
        raise NotImplementedError()

    def cancel(self):
        """Stop listening on the event bus"""
        HABApp.core.EventBus.remove_listener(self)

        # If we have a context remove the listener from there, too
        if self._habapp_rule_ctx is not None:
            self._habapp_rule_ctx.remove_event_listener(self)
            self._habapp_rule_ctx = None
