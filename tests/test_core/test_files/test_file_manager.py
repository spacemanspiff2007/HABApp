from collections.abc import Awaitable, Callable
from pathlib import Path
from unittest.mock import Mock

import pytest

import HABApp
from HABApp.core.const.topics import TOPIC_FILES
from HABApp.core.events.habapp_events import RequestFileLoadEvent, RequestFileUnloadEvent
from HABApp.core.files import FileManager
from HABApp.core.files import manager as file_manager_module
from HABApp.core.files.errors import AlreadyHandledFileError
from HABApp.core.files.file import FileProperties, FileState, HABAppFile
from HABApp.core.files.manager import log as file_manager_logger
from HABApp.core.internals import EventBus
from tests.helpers import LogCollector


async def test_file_watcher_event(monkeypatch, file_manager, test_logs: LogCollector) -> None:
    test_logs.set_min_level(0)

    file_manager.add_folder('tests-', Path('tests/'), name='d', priority=1)

    eb = Mock(EventBus)
    eb.post_event = Mock()
    eb.post_event.assert_not_called()
    monkeypatch.setattr(HABApp.core, 'EventBus', eb, raising=False)

    path_instance = Mock()
    path_instance.is_dir = Mock(return_value=False)
    monkeypatch.setattr(file_manager_module, 'Path', Mock(return_value=path_instance))

    # Unload
    path_instance.is_file = Mock(return_value=False)
    await file_manager.file_watcher_event('tests/asdf')
    eb.post_event.assert_called_once_with(TOPIC_FILES, RequestFileUnloadEvent('tests-asdf'))
    eb.post_event.reset_mock()

    # Load
    path_instance.is_file = Mock(return_value=True)
    await file_manager.file_watcher_event('tests/asdf')
    eb.post_event.assert_called_once_with(TOPIC_FILES, RequestFileLoadEvent('tests-asdf'))
    eb.post_event.reset_mock()

    # Skip load (checksum)
    file_manager._files['tests-asdf'] = f1 = HABAppFile('tests-asdf', Path('path1'), b'checksum', FileProperties())
    monkeypatch.setattr(HABAppFile, 'create_checksum', lambda x: b'checksum')
    await file_manager.file_watcher_event('tests/asdf')
    eb.post_event.assert_not_called()

    test_logs.add_expected(
        file_manager_module.log.name, 'DEBUG', 'Skip file system event because file tests-asdf did not change')
    test_logs.assert_ok()


def setup_file(file_manager: FileManager, *, set_state: bool = True,
               on_load: Callable[[str, Path], Awaitable[None]] | None = None,
               on_unload: Callable[[str, Path], Awaitable[None]] | None = None) -> HABAppFile:

    file_manager._files.clear()
    file_manager._files['name1'] = f1 = HABAppFile('name1', Path('path1'), b'checksum', FileProperties())

    if set_state:
        f1._state = FileState.DEPENDENCIES_OK

    file_manager._file_handlers = ()
    file_manager.add_handler('myhandler', logger=file_manager_logger, prefix='n', on_load=on_load, on_unload=on_unload)

    return f1


async def test_load(test_logs: LogCollector, file_manager) -> None:
    setup_file(file_manager, set_state=False)
    with pytest.raises(ValueError) as e:
        await file_manager._do_file_load('name1')
    assert str(e.value) == 'File name1 can not be loaded because current state is PENDING!'

    async def coro(name: str, path: Path) -> None:
        pass

    f = setup_file(file_manager, on_load=coro)
    await file_manager._do_file_load('name1')
    assert f._state is FileState.LOADED

    # Error in coro -> state should be Failed
    async def coro(name: str, path: Path) -> None:
        raise AlreadyHandledFileError()

    f = setup_file(file_manager, on_load=coro)
    await file_manager._do_file_load('name1')
    assert f._state is FileState.FAILED
    test_logs.assert_ok()


async def test_unload(test_logs: LogCollector, file_manager) -> None:
    async def coro(name: str, path: Path) -> None:
        pass

    # Remove should work regardless of state
    f = setup_file(file_manager, set_state=False, on_unload=coro)
    await file_manager._do_file_unload('name1')
    assert f._state is FileState.REMOVED
    assert file_manager.get_file('name1') is None

    f = setup_file(file_manager, on_unload=coro)
    await file_manager._do_file_unload('name1')
    assert f._state is FileState.REMOVED
    assert file_manager.get_file('name1') is None

    # Error in coro -> state should be Failed
    async def coro(name: str, path: Path) -> None:
        raise AlreadyHandledFileError()

    f = setup_file(file_manager, on_unload=coro)
    await file_manager._do_file_unload('name1')
    assert f._state is FileState.FAILED
    test_logs.assert_ok()
