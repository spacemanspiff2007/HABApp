from pathlib import Path

import pytest

from HABApp.core.files.file import CircularReferenceError, FileProperties, FileState, HABAppFile
from HABApp.core.files.manager import log as file_manager_logger
from tests.helpers import LogCollector


@pytest.fixture
def files(file_manager) -> dict[str, HABAppFile]:
    assert not file_manager._files
    return file_manager._files


def test_depends(test_logs: LogCollector, files, file_manager) -> None:
    files['name1'] = f1 = HABAppFile('name1', Path('path1'), b'checksum', FileProperties(depends_on=['name2']))
    files['name2'] = f2 = HABAppFile('name2', Path('path2'), b'checksum', FileProperties())

    f1.check_properties(file_manager, file_manager_logger, log_msg=True)
    f2.check_properties(file_manager, file_manager_logger, log_msg=True)

    assert f1._state is FileState.DEPENDENCIES_MISSING
    assert f2._state is FileState.DEPENDENCIES_OK

    f2._state = FileState.LOADED
    f1.check_dependencies(file_manager)
    assert f1._state is FileState.DEPENDENCIES_OK

    files['name3'] = f3 = HABAppFile('name3', Path('path3'), b'checksum', FileProperties(depends_on=['asdf']))
    f3.check_properties(file_manager, file_manager_logger, log_msg=True)
    test_logs.add_expected('HABApp.files', 'ERROR', "File path3 depends on file that doesn't exist: asdf")


def test_reloads(test_logs: LogCollector, files, file_manager) -> None:
    files['name1'] = f1 = HABAppFile('name1', Path('path1'), b'checksum', FileProperties(reloads_on=['name2', 'asdf']))
    files['name2'] = f2 = HABAppFile('name2', Path('path2'), b'checksum', FileProperties())

    f1.check_properties(file_manager, file_manager_logger)
    assert f1.properties.reloads_on == ['name2', 'asdf']
    assert f2.properties.reloads_on == []

    test_logs.add_expected('HABApp.files', 'WARNING', "File path1 reloads on file that doesn't exist: asdf")


def test_circ(test_logs: LogCollector, files, file_manager) -> None:
    files['name1'] = f1 = HABAppFile('name1', Path('path1'), b'checksum', FileProperties(depends_on=['name2']))
    files['name2'] = f2 = HABAppFile('name2', Path('path2'), b'checksum', FileProperties(depends_on=['name3']))
    files['name3'] = f3 = HABAppFile('name3', Path('path3'), b'checksum', FileProperties(depends_on=['name1']))

    with pytest.raises(CircularReferenceError) as e:
        f1._check_circ_refs((f1.name,), 'depends_on', file_manager)
    assert e.value.stack == ('name1', 'name2', 'name3', 'name1')

    # Check log output
    f1.check_properties(file_manager, file_manager_logger)
    test_logs.add_expected('HABApp.files', 'ERROR', 'Circular reference: name1 -> name2 -> name3 -> name1')

    with pytest.raises(CircularReferenceError) as e:
        f2._check_circ_refs((f2.name,), 'depends_on', file_manager)
    assert e.value.stack == ('name2', 'name3', 'name1', 'name2',)

    with pytest.raises(CircularReferenceError) as e:
        f3._check_circ_refs((f3.name,), 'depends_on', file_manager)
    assert e.value.stack == ('name3', 'name1', 'name2', 'name3', )
