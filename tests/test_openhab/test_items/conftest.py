from typing import Literal

import pytest

from HABApp.openhab.definitions.websockets import ItemCommandSendEvent, ItemStateSendEvent
from HABApp.openhab.definitions.websockets import base as websocket_base_module
from HABApp.openhab.items import base_item as base_item_module


class ValueCollector:
    def __init__(self) -> None:
        self.values = []

    def __call__(self, event: ItemCommandSendEvent | ItemStateSendEvent) -> None:
        self.values.append(event)

    def assert_called_once(self, type: str, value: str, *, event: Literal['command', 'update'], clear: bool = True):
        assert len(self.values) == 1
        obj = self.values[0]
        assert isinstance(obj, {'command': ItemCommandSendEvent, 'update': ItemStateSendEvent}[event])
        assert obj.payload.type == type
        assert obj.payload.value == value

        if clear:
            self.values.clear()


@pytest.fixture
def websocket_events(monkeypatch) -> ValueCollector:
    c = ValueCollector()
    monkeypatch.setattr(base_item_module, 'send_websocket_event', c)
    return c


@pytest.fixture(autouse=True)
def patch_event_id(monkeypatch):
    monkeypatch.setattr(websocket_base_module, 'MSG_CTR', 1)
