class EventBusBaseListener:
    def __init__(self, topic: str):
        assert isinstance(topic, str)
        self.topic: str = topic

    def notify_listeners(self, event):
        raise NotImplementedError()

    def describe(self) -> str:
        raise NotImplementedError()
