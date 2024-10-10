from typing import Any, Final


class EventBusBaseListener:
    def __init__(self, topic: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not isinstance(topic, str):
            raise TypeError()
        if not topic:
            raise ValueError()
        self.topic: Final = topic

    def notify_listeners(self, event: Any) -> None:
        raise NotImplementedError()

    def describe(self) -> str:
        raise NotImplementedError()
