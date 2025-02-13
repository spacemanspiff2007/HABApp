import logging
from pathlib import PurePath

import pytest
from typing_extensions import Self
from watchfiles import Change

from HABApp.core.const.const import PYTHON_312
from HABApp.core.files import HABAppFileWatcher
from HABApp.core.files import watcher as watcher_module


class MyPath(PurePath):

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self._is_dir = False
        self._is_file = False

    def is_dir(self) -> bool:
        return self._is_dir

    def is_file(self) -> bool:
        return self._is_file

    def set_is_dir(self, value: bool) -> Self:
        self._is_dir = value
        return self

    def set_is_file(self, value: bool) -> Self:
        self._is_file = value
        return self


@pytest.mark.skipif(not PYTHON_312, reason='Subclassing Path requires Python 3.12!')
async def test_watcher(monkeypatch, test_logs) -> None:
    logging.getLogger('HABApp.file.events').setLevel(0)
    test_logs.set_min_level(0)

    f = HABAppFileWatcher()
    f._watcher_task = lambda: 'ReplacedTask'
    monkeypatch.setattr(watcher_module, 'create_task_from_async', lambda x: x)

    with pytest.raises(FileNotFoundError) as e:
        f.add_path(MyPath('a/b/c'))
    assert str(e.value) in ('Path a/b/c does not exist', 'Path a\\b\\c does not exist')

    async def coro(text: str):
        raise ValueError()

    f.watch_folder('folder1', coro, MyPath('my/folder/1').set_is_dir(True))

    assert not f._watch_filter(Change.added, 'my/folder/2/file1')
    assert not f._watch_filter(Change.added, 'my/folder/2/file1', dispatchers=f._dispatchers)

    test_logs.add_expected('HABApp.file.events', 'DEBUG', 'Added dispatcher folder1')
    test_logs.add_expected('HABApp.file.events', 'DEBUG', 'Watching my\\folder\\1')
    test_logs.add_expected('HABApp.file.events', 'DEBUG', 'added my/folder/2/file1')
    test_logs.assert_ok()
