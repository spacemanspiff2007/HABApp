import logging
from asyncio import sleep
from pathlib import Path

import pytest

import HABApp
from HABApp.core.files.file.file import FileProperties, HABAppFile
from HABApp.core.files.folders import add_folder
from HABApp.core.files.folders.folders import FOLDERS
from HABApp.core.files.manager import process_file
from tests.helpers import LogCollector


class MockFile:
    def __init__(self, name: str):
        self.name = name.split('/')[1]

    def as_posix(self):
        return f'/my_param/{self.name}'

    def is_file(self):
        return True

    def __repr__(self):
        return f'<MockFile {self.name}>'


class CfgObj:
    def __init__(self):
        self.properties = {}
        self.operation: list[tuple[str, str]] = []

        class TestFile(HABAppFile):
            LOGGER = logging.getLogger('test')
            LOAD_FUNC = self.load_file
            UNLOAD_FUNC = self.unload_file
        self.cls = TestFile

    async def load_file(self, name: str, path: Path):
        self.operation.append(('load', name))

    async def unload_file(self, name: str, path: Path):
        self.operation.append(('unload', name))

    async def wait_complete(self):
        while HABApp.core.files.manager.worker.TASK is not None:
            await sleep(0.05)

    async def process_file(self, name: str):
        await process_file(name, MockFile(name))

    def create_file(self, name, path) -> HABAppFile:
        return self.cls(name, MockFile(name), self.properties[name])


@pytest.fixture()
def cfg(monkeypatch):
    obj = CfgObj()

    monkeypatch.setattr(HABApp.core.files.manager.worker, 'TASK_SLEEP', 0.001)
    monkeypatch.setattr(HABApp.core.files.manager.worker, 'TASK_DURATION', 0.001)
    monkeypatch.setattr(HABApp.core.files.file, 'create_file', obj.create_file)

    FOLDERS.clear()
    add_folder('rules/', Path('c:/HABApp/my_rules/'), 0)
    add_folder('configs/', Path('c:/HABApp/my_config/'), 10)
    add_folder('params/', Path('c:/HABApp/my_param/'), 20)

    yield obj

    FOLDERS.clear()


# def test_reload_on(cfg, sync_worker, event_bus: TmpEventBus):
#     order = []
#
#     def process_event(event):
#         order.append(event.name)
#         file_load_ok(event.name)
#
#     FILE_PROPS.clear()
#     FILE_PROPS['params/param1'] = FileProperties(depends_on=[], reloads_on=['params/param2'])
#     FILE_PROPS['params/param2'] = FileProperties()
#
#     event_bus.listen_events(HABApp.core.const.topics.TOPIC_FILES, process_event)
#
#     process([MockFile('param2'), MockFile('param1')])
#
#     assert order == ['params/param1', 'params/param2', 'params/param1']
#     order.clear()
#
#     process([])
#     assert order == []
#
#     process([MockFile('param2')])
#     assert order == ['params/param2', 'params/param1']
#     order.clear()
#
#     process([MockFile('param1')])
#     assert order == ['params/param1']
#     order.clear()
#
#     process([MockFile('param2')])
#     assert order == ['params/param2', 'params/param1']
#     order.clear()


async def test_reload_dep(cfg: CfgObj, caplog):
    cfg.properties['params/param1'] = FileProperties(depends_on=['params/param2'], reloads_on=['params/param2'])
    cfg.properties['params/param2'] = FileProperties()

    await cfg.process_file('params/param1')
    await cfg.process_file('params/param2')
    await cfg.wait_complete()

    assert cfg.operation == [('load', 'params/param2'), ('load', 'params/param1')]
    cfg.operation.clear()

    await cfg.process_file('params/param2')
    await cfg.wait_complete()
    assert cfg.operation == [('load', 'params/param2'), ('load', 'params/param1')]
    cfg.operation.clear()

    await cfg.process_file('params/param1')
    await cfg.wait_complete()
    assert cfg.operation == [('load', 'params/param1')]
    cfg.operation.clear()

    await cfg.process_file('params/param2')
    await cfg.wait_complete()
    assert cfg.operation == [('load', 'params/param2'), ('load', 'params/param1')]
    cfg.operation.clear()


async def test_missing_dependencies(cfg: CfgObj, test_logs: LogCollector):
    cfg.properties['params/param1'] = FileProperties(depends_on=['params/param4', 'params/param5'])
    cfg.properties['params/param2'] = FileProperties(depends_on=['params/param4'])
    cfg.properties['params/param3'] = FileProperties()

    await cfg.process_file('params/param1')
    await cfg.process_file('params/param2')
    await cfg.process_file('params/param3')
    await cfg.wait_complete()

    assert cfg.operation == [('load', 'params/param3')]

    msg1 = (
        'HABApp.files', logging.ERROR, "File <MockFile param2> depends on file that doesn't exist: params/param4"
    )
    msg2 = (
        'HABApp.files', logging.ERROR,
        "File <MockFile param1> depends on files that don't exist: params/param4, params/param5"
    )

    test_logs.add_expected(*msg1)
    test_logs.add_expected(*msg2)


# def test_missing_loads(cfg, sync_worker, event_bus: TmpEventBus, caplog):
#     order = []
#
#     def process_event(event):
#         order.append(event.name)
#         file_load_ok(event.name)
#
#     FILE_PROPS['params/param1'] = FileProperties(reloads_on=['params/param4', 'params/param5'])
#     FILE_PROPS['params/param2'] = FileProperties(reloads_on=['params/param4'])
#
#     event_bus.listen_events(HABApp.core.const.topics.TOPIC_FILES, process_event)
#
#     process([MockFile('param1'), MockFile('param2')])
#
#     assert order == ['params/param1', 'params/param2']
#     order.clear()
#
#     process([])
#     assert order == []
#
#     msg1 = (
#         'HABApp.files', logging.WARNING, "File <MockFile param2> reloads on file that doesn't exist: params/param4"
#     )
#     msg2 = ('HABApp.files', logging.WARNING,
#             "File <MockFile param1> reloads on files that don't exist: params/param4, params/param5")
#
#     assert msg1 in caplog.record_tuples
#     assert msg2 in caplog.record_tuples
#
#
# def test_load_continue_after_missing(cfg, sync_worker, event_bus: TmpEventBus, caplog):
#     order = []
#
#     def process_event(event):
#         order.append(event.name)
#         file_load_ok(event.name)
#
#     FILE_PROPS.clear()
#     FILE_PROPS['params/p1'] = FileProperties(depends_on=['params/p2'], reloads_on=[])
#     FILE_PROPS['params/p2'] = FileProperties()
#
#     event_bus.listen_events(HABApp.core.const.topics.TOPIC_FILES, process_event)
#
#     process([MockFile('p1')])
#
#     # File can not be loaded
#     assert order == []
#
#     # Add missing file
#     process([MockFile('p2')])
#
#     # Both files get loaded
#     assert order == ['params/p2', 'params/p1']
