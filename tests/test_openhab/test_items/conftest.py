from collections.abc import Generator
from typing import Any, Literal

import pytest

from HABApp.openhab.definitions.websockets import ItemCommandSendEvent, ItemStateSendEvent
from HABApp.openhab.definitions.websockets import base as websocket_base_module
from HABApp.openhab.item_factory import OhItemFactory


class ValueCollector:
    def __init__(self) -> None:
        self.values = []

    def __call__(self, event: ItemCommandSendEvent | ItemStateSendEvent) -> None:
        self.values.append(event)

    def assert_called_once(self, type: str, value: str, *, event: Literal['command', 'update'], clear: bool = True) -> None:
        assert len(self.values) == 1
        obj = self.values[0]
        assert isinstance(obj, {'command': ItemCommandSendEvent, 'update': ItemStateSendEvent}[event])
        assert obj.payload.type == type
        assert obj.payload.value == value

        if clear:
            self.values.clear()


@pytest.fixture
def websocket_events(oh_interface) -> Generator[ValueCollector, Any, None]:

    v = ValueCollector()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(oh_interface, '_send_websocket_event', v)
        yield v


@pytest.fixture(autouse=True)
def patch_event_id(monkeypatch) -> None:
    monkeypatch.setattr(websocket_base_module, 'MSG_CTR', 1)


@pytest.fixture
def item_factory() -> OhItemFactory:
    return OhItemFactory(None, None, None)
