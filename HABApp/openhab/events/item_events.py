import HABApp.core

from .map_events import map_event_types
from .base_event import BaseItemEvent


class ItemStateEvent(BaseItemEvent, HABApp.core.ValueUpdateEvent):
    def __init__(self, _in_dict):
        super().__init__(_in_dict)

        # smarthome/items/NAME/state
        self.name = self._topic[16:-6]
        self.value = map_event_types(self._payload['type'], self._payload['value'])

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class ItemStateChangedEvent(BaseItemEvent, HABApp.core.ValueChangeEvent):
    def __init__(self, _in_dict):
        super().__init__(_in_dict)

        # smarthome/items/Ping/statechanged
        self.name = self._topic[16:-13]
        self.value = map_event_types(self._payload['type'], self._payload['value'])
        self.old_value = map_event_types(self._payload['oldType'], self._payload['oldValue'])

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}, old_value: {self.old_value}>'


class ItemCommandEvent(BaseItemEvent):
    def __init__(self, _in_dict):
        super().__init__(_in_dict)

        # smarthome/items/NAME/command
        self.name = self._topic[16:-8]
        self.value = map_event_types(self._payload['type'], self._payload['value'])

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class ItemAddedEvent(BaseItemEvent):
    def __init__(self, _in_dict):
        super().__init__(_in_dict)

        # {'topic': 'smarthome/items/NAME/added'
        # 'payload': '{"type":"Contact","name":"Test","tags":[],"groupNames":[]}'
        # 'type': 'ItemAddedEvent'}
        self.name = self._payload['name']
        self.type = self._payload['type']

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, type: {self.type}>'


class ItemUpdatedEvent(BaseItemEvent):
    def __init__(self, _in_dict):
        super().__init__(_in_dict)

        # smarthome/items/NAME/updated
        # 'payload': '[{"type":"Switch","name":"Test","tags":[],"groupNames":[]},
        #              {"type":"Contact","name":"Test","tags":[],"groupNames":[]}]',
        # 'type': 'ItemUpdatedEvent'
        self.name = self._topic[16:-8]
        self.type = self._payload[1]['type']

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, type: {self.type}>'


class ItemRemovedEvent(BaseItemEvent):
    def __init__(self, _in_dict):
        super().__init__(_in_dict)

        # smarthome/items/Test/removed
        self.name = self._topic[16:-8]

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}>'


class ItemStatePredictedEvent(BaseItemEvent):
    def __init__(self, _in_dict):
        super().__init__(_in_dict)

        # 'smarthome/items/NAME/statepredicted'
        self.name = self._topic[16:-15]
        self.value = map_event_types(self._payload['predictedType'], self._payload['predictedValue'])

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class GroupItemStateChangedEvent(BaseItemEvent):
    def __init__(self, _in_dict):
        super().__init__(_in_dict)

        # 'smarthome/items/TestGroupAVG/TestNumber1/statechanged'
        parts = self._topic.split('/')
        self.name = parts[2]
        self.item = parts[3]

        self.value = map_event_types(self._payload['type'], self._payload['value'])
        self.old_value = map_event_types(self._payload['oldType'], self._payload['oldValue'])

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}, old_value: {self.old_value}>'
