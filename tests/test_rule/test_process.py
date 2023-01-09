import asyncio
import sys
from json import loads
from pathlib import Path
from unittest.mock import Mock

import pytest

import HABApp.rule
from HABApp.rule import Rule, FinishedProcessInfo
from HABApp.rule.interfaces import rule_subprocess
from ..helpers import LogCollector
from ..rule_runner import SimpleRuleRunner


class ProcRule(Rule):
    def __init__(self):
        super().__init__()
        self.cb = Mock()
        self.cb.__name__ = 'mock_callback'


@pytest.fixture(scope="function")
def rule(monkeypatch):
    monkeypatch.setattr(HABApp.CONFIG, '_file_path', Path(__file__).with_name('config.yml'))

    runner = SimpleRuleRunner()
    runner.set_up()

    rule = ProcRule()

    yield rule

    runner.tear_down()


SLEEP_PROCESS_START = 0.3


@pytest.mark.no_internals
async def test_run_func_arg_errors(rule):
    with pytest.raises(ValueError) as e:
        rule.execute_subprocess(rule.cb, sys.executable, "asfd", 123)
    assert str(e.value) == 'args[2] is not of type str! "123" (int)'

    with pytest.raises(ValueError) as e:
        rule.execute_subprocess(
            rule.cb, sys.executable, "asfd", additional_python_path=[Path(__file__).parent, 123]
        )
    assert str(e.value) == 'additional_python_path[1] is not of type str! "123" (int)'


@pytest.mark.parametrize('flag,result', [[True, FinishedProcessInfo(0, 'OK', '')], [False, 'OK']])
@pytest.mark.no_internals
async def test_run_func(rule, flag, result):

    rule.execute_subprocess(
        rule.cb, sys.executable, '-c', 'import datetime; print("OK", end="")', capture_output=True, raw_info=flag
    )

    await asyncio.sleep(SLEEP_PROCESS_START)
    rule.cb.assert_called_once_with(result)


@pytest.mark.parametrize('flag,result', [[True, FinishedProcessInfo(0, None, None)], [False, '']])
@pytest.mark.no_internals
async def test_run_func_no_cap(rule, flag: bool, result):
    rule.execute_subprocess(
        rule.cb, sys.executable, '-c', 'import datetime; print("OK", end="")', capture_output=False, raw_info=flag
    )

    await asyncio.sleep(SLEEP_PROCESS_START)
    rule.cb.assert_called_once_with(FinishedProcessInfo(0, None, None))


@pytest.mark.parametrize('flag,result', [[True, FinishedProcessInfo(0, None, None)], [False, '']])
@pytest.mark.no_internals
async def test_run_func_cancel(rule, flag, result, test_logs: LogCollector):

    task = rule.execute_subprocess(
        rule.cb, sys.executable, '-c', 'import time; time.sleep(5)', capture_output=False, raw_info=flag
    )
    await asyncio.sleep(SLEEP_PROCESS_START)

    task.cancel()

    await asyncio.sleep(SLEEP_PROCESS_START)
    rule.cb.assert_not_called()

    test_logs.add_expected(
        None, 'WARNING',
        f'Subprocess canceled! Call: "{sys.executable:s}" "-c" "import time; time.sleep(5)"'
    )


@pytest.mark.parametrize('flag', [True, False])
@pytest.mark.no_internals
async def test_invalid_program(rule, test_logs, flag):
    parent_dir = Path(__file__).parent
    rule.execute_subprocess(rule.cb, 'ProgramThatDoesNotExist', capture_output=True, raw_info=flag)
    await asyncio.sleep(SLEEP_PROCESS_START)

    test_logs.add_expected(None, 'ERROR', [
        'Creating subprocess failed!',
        '  Call: "ProgramThatDoesNotExist"',
        f'  Working dir: {parent_dir}',
        None,
    ])

    rule.cb.assert_not_called()


@pytest.mark.parametrize('raw_info', [True, False])
@pytest.mark.no_internals
async def test_exec_python_file(rule, caplog, raw_info):
    parent_dir = Path(__file__).parent

    rule.execute_python(rule.cb, parent_dir / '__exec_python_file.py', capture_output=True, raw_info=raw_info)
    await asyncio.sleep(SLEEP_PROCESS_START)

    rule.cb.assert_called_once()
    ret = rule.cb.call_args[0][0]

    if raw_info:
        assert ret.stderr == ''
        assert ret.returncode == 0
        _json = loads(ret.stdout)
    else:
        _json = loads(ret)

    assert _json['cwd'] == str(parent_dir)


@pytest.mark.no_internals
async def test_exec_python_file_relative(rule):
    parent_dir = Path(__file__).parent

    rule.execute_python(rule.cb, '__exec_python_file.py', capture_output=True)
    await asyncio.sleep(SLEEP_PROCESS_START)

    rule.cb.assert_called_once()
    _json = loads(rule.cb.call_args[0][0])
    assert _json['cwd'] == str(parent_dir)


@pytest.mark.no_internals
async def test_exec_python_file_error_stderr(rule, test_logs: LogCollector):
    folder = Path(__file__).parent
    file = folder / '__exec_python_file.py'

    rule.execute_python(rule.cb, file, 'show_err', capture_output=True, additional_python_path=[folder])
    await asyncio.sleep(SLEEP_PROCESS_START)

    test_logs.add_expected(None, 'ERROR', [
        'Process returned 1!',
        None,
        'Stderr:',
        '  Error in module!',
    ])

    rule.cb.assert_not_called()


@pytest.mark.no_internals
async def test_exec_python_file_error_stdout(rule, test_logs: LogCollector):
    folder = Path(__file__).parent
    file = folder / '__exec_python_file.py'
    rule.execute_python(rule.cb, file, 'exit_3', capture_output=True, additional_python_path=[folder])
    await asyncio.sleep(SLEEP_PROCESS_START)

    test_logs.add_expected(None, 'ERROR', [
        'Process returned 3!',
        None,
        'Stdout:',
        '  Error Message 3'
    ])
    rule.cb.assert_not_called()


@pytest.mark.parametrize('raw_info, result', [[True, FinishedProcessInfo(0, 'module ok', '')], [False, 'module ok']])
@pytest.mark.no_internals
async def test_exec_python_module(rule, raw_info, result):
    folder = Path(__file__).parent
    rule.execute_python(
        rule.cb, '__exec_python_module', capture_output=True, additional_python_path=[folder], raw_info=raw_info)
    await asyncio.sleep(SLEEP_PROCESS_START)

    rule.cb.assert_called_once_with(result)


@pytest.mark.no_internals
def test_param_pythonpath(monkeypatch):
    monkeypatch.setattr(HABApp.CONFIG, '_file_path', Path(__file__))
    folder = str(Path(__file__).parent)

    env = {}
    monkeypatch.setattr(rule_subprocess.os, 'environ', env)

    # Check set
    args, kwargs = rule_subprocess.build_exec_params(_additional_python_path=[folder])
    assert kwargs['env']['PYTHONPATH'] == folder

    # Check append
    env['PYTHONPATH'] = 'existing/folder'
    args, kwargs = rule_subprocess.build_exec_params(_additional_python_path=[folder])
    assert kwargs['env']['PYTHONPATH'] == f'{folder};existing/folder' or f'{folder}:existing/folder'

    # Absolute path required
    with pytest.raises(ValueError) as e:
        rule_subprocess.build_exec_params(_additional_python_path=['asdf/asdf'])
    assert str(e.value) == 'additional_python_path[0] is not an absolute path: "asdf/asdf"'
