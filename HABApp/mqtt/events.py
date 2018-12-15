
class MqttEvent:
    def __init__(self, topic, value):
        self.topic = topic
        self.value = value
        
    def __repr__(self):
        return f'<{self.__class__.__name__} topic: {self.topic}, value: {self.value}>'

class MqttUpdate(MqttEvent):
    pass

class MqttChange(MqttEvent):
    pass