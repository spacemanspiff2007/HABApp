import logging
from pathlib import Path

import pytest

import HABApp
from HABApp.core.files.all import file_load_ok, process
from HABApp.core.files.file import FileProperties, HABAppFile
from ...helpers import TmpEventBus

FILE_PROPS = {}


@classmethod
def from_path(cls, name: str, path) -> HABAppFile:
    return cls(name, MockFile(name), FILE_PROPS[name])


class MockFile:
    def __init__(self, name: str):
        if name.startswith('params/'):
            name = name[7:]
        self.name = name

    def as_posix(self):
        return f'/my_param/{self.name}'

    def is_file(self):
        return True

    def __repr__(self):
        return f'<MockFile {self.name}>'


@pytest.fixture
def cfg(monkeypatch):
    monkeypatch.setattr(HABAppFile, 'from_path', from_path)
    monkeypatch.setattr(HABApp.config.CONFIG.directories, 'rules', Path('/my_rules/'))
    monkeypatch.setattr(HABApp.config.CONFIG.directories, 'config', Path('/my_config/'))
    monkeypatch.setattr(HABApp.config.CONFIG.directories, 'param', Path('/my_param/'))

    yield


def test_reload_on(cfg, sync_worker, event_bus: TmpEventBus):
    order = []

    def process_event(event):
        order.append(event.name)
        file_load_ok(event.name)

    FILE_PROPS.clear()
    FILE_PROPS['params/param1'] = FileProperties(depends_on=[], reloads_on=['params/param2'])
    FILE_PROPS['params/param2'] = FileProperties()

    event_bus.listen_events(HABApp.core.const.topics.FILES, process_event)

    process([MockFile('param2'), MockFile('param1')])

    assert order == ['params/param1', 'params/param2', 'params/param1']
    order.clear()

    process([])
    assert order == []

    process([MockFile('param2')])
    assert order == ['params/param2', 'params/param1']
    order.clear()

    process([MockFile('param1')])
    assert order == ['params/param1']
    order.clear()

    process([MockFile('param2')])
    assert order == ['params/param2', 'params/param1']
    order.clear()


def test_reload_dep(cfg, sync_worker, event_bus: TmpEventBus):
    order = []

    def process_event(event):
        order.append(event.name)
        file_load_ok(event.name)

    FILE_PROPS.clear()
    FILE_PROPS['params/param1'] = FileProperties(depends_on=['params/param2'], reloads_on=['params/param2'])
    FILE_PROPS['params/param2'] = FileProperties()

    event_bus.listen_events(HABApp.core.const.topics.FILES, process_event)

    process([MockFile('param2'), MockFile('param1')])

    assert order == ['params/param2', 'params/param1']
    order.clear()

    process([])
    assert order == []

    process([MockFile('param2')])
    assert order == ['params/param2', 'params/param1']
    order.clear()

    process([MockFile('param1')])
    assert order == ['params/param1']
    order.clear()

    process([MockFile('param2')])
    assert order == ['params/param2', 'params/param1']
    order.clear()


def test_missing_dependencies(cfg, sync_worker, event_bus: TmpEventBus, caplog):
    order = []

    def process_event(event):
        order.append(event.name)
        file_load_ok(event.name)

    FILE_PROPS['params/param1'] = FileProperties(depends_on=['params/param4', 'params/param5'])
    FILE_PROPS['params/param2'] = FileProperties(depends_on=['params/param4'])
    FILE_PROPS['params/param3'] = FileProperties()

    event_bus.listen_events(HABApp.core.const.topics.FILES, process_event)

    process([MockFile('param1'), MockFile('param2'), MockFile('param3')])

    assert order == ['params/param3']
    order.clear()

    process([])
    assert order == []

    msg1 = (
        'HABApp.files', logging.ERROR, "File <MockFile param2> depends on file that doesn't exist: params/param4"
    )
    msg2 = (
        'HABApp.files', logging.ERROR,
        "File <MockFile param1> depends on files that don't exist: params/param4, params/param5"
    )

    assert msg1 in caplog.record_tuples
    assert msg2 in caplog.record_tuples


def test_missing_loads(cfg, sync_worker, event_bus: TmpEventBus, caplog):
    order = []

    def process_event(event):
        order.append(event.name)
        file_load_ok(event.name)

    FILE_PROPS['params/param1'] = FileProperties(reloads_on=['params/param4', 'params/param5'])
    FILE_PROPS['params/param2'] = FileProperties(reloads_on=['params/param4'])

    event_bus.listen_events(HABApp.core.const.topics.FILES, process_event)

    process([MockFile('param1'), MockFile('param2')])

    assert order == ['params/param1', 'params/param2']
    order.clear()

    process([])
    assert order == []

    msg1 = (
        'HABApp.files', logging.WARNING, "File <MockFile param2> reloads on file that doesn't exist: params/param4"
    )
    msg2 = ('HABApp.files', logging.WARNING,
            "File <MockFile param1> reloads on files that don't exist: params/param4, params/param5")

    assert msg1 in caplog.record_tuples
    assert msg2 in caplog.record_tuples
