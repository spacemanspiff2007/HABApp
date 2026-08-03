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


def test_reloads_on_state_transition(files, file_manager) -> None:
    """A dependent file must transition correctly when a reloads_on target changes,
    and a second cascade must not overwrite UNLOAD_PENDING (regression, see race condition)."""

    files['dep'] = dep = HABAppFile('dep', Path('dep'), b'ch', FileProperties())
    files['rule'] = rule = HABAppFile('rule', Path('rule'), b'ch', FileProperties(reloads_on=['dep']))

    # 1) First cascade: a LOADED dependent must go to UNLOAD_PENDING
    rule._state = FileState.LOADED
    rule.file_state_changed(dep, file_manager)
    assert rule._state is FileState.UNLOAD_PENDING

    # 2) A second cascade while UNLOAD_PENDING must NOT overwrite it with PENDING,
    #    otherwise the unload handler would be skipped and the old instance orphaned.
    rule.file_state_changed(dep, file_manager)
    assert rule._state is FileState.UNLOAD_PENDING

    # 3) Pre-load states are re-evaluated -> PENDING
    for state in (FileState.DEPENDENCIES_OK, FileState.DEPENDENCIES_MISSING, FileState.DEPENDENCIES_ERROR):
        rule._state = state
        rule.file_state_changed(dep, file_manager)
        assert rule._state is FileState.PENDING

    # 4) States that must be left untouched by a reload cascade
    for state in (FileState.PENDING, FileState.FAILED, FileState.REMOVED, FileState.PROPERTIES_INVALID):
        rule._state = state
        rule.file_state_changed(dep, file_manager)
        assert rule._state is state

    # 5) A file that does not reload on 'dep' is never affected
    files['other'] = other = HABAppFile('other', Path('other'), b'ch', FileProperties())
    other._state = FileState.LOADED
    other.file_state_changed(dep, file_manager)
    assert other._state is FileState.LOADED
