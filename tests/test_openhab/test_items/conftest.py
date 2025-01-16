import pytest

from HABApp.openhab.items import base_item as base_item_module


class ValueCollector:
    def __init__(self):
        self.values = []

    def __call__(self, name, value):
        self.values.append(value)

    def assert_called_with(self, *values, clear=True):
        if len(values) == 1 and len(self.values) == 1:
            assert self.values[0] == values[0]

        assert self.values == list(values)
        if clear:
            self.values.clear()


@pytest.fixture
def sent_commands(monkeypatch) -> ValueCollector:
    c = ValueCollector()
    monkeypatch.setattr(base_item_module, 'send_command', c)
    return c


@pytest.fixture
def posted_updates(monkeypatch) -> ValueCollector:
    c = ValueCollector()
    monkeypatch.setattr(base_item_module, 'post_update', c)
    return c
