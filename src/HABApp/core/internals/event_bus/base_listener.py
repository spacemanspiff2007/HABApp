class EventBusBaseListener:
    def __init__(self, topic: str, **kwargs):
        super().__init__(**kwargs)
        assert isinstance(topic, str)
        self.topic: str = topic

    def notify_listeners(self, event):
        raise NotImplementedError()

    def describe(self) -> str:
        raise NotImplementedError()
