from typing import Optional, TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
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
        raise NotImplementedError()


TYPE_EVENT_BUS_LISTENER = TypeVar('TYPE_EVENT_BUS_LISTENER', bound=EventBusListenerBase)
