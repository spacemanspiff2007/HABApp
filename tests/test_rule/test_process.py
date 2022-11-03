import asyncio
import sys
from json import loads
from pathlib import Path

import pytest

from HABApp.rule import Rule
from HABApp.rule.interfaces import rule_subprocess
from ..rule_runner import SimpleRuleRunner


class ProcRule(Rule):
    def __init__(self):
        super().__init__()
        self.ret = None

    def set_ret(self, value):
        self.ret = value


@pytest.fixture(scope="function")
def rule():
    runner = SimpleRuleRunner()
    runner.set_up()

    rule = ProcRule()

    yield rule

    runner.tear_down()


@pytest.mark.no_internals
async def test_run_func(rule):
    rule.execute_subprocess(
        rule.set_ret, sys.executable, '-c', 'import datetime; print("OK", end="")', capture_output=True
    )

    await asyncio.sleep(0.5)
    assert rule.ret.returncode == 0
    assert rule.ret.stdout == 'OK'
    assert rule.ret.stderr == ''


@pytest.mark.no_internals
async def test_run_func_no_cap(rule):
    rule.execute_subprocess(
        rule.set_ret, sys.executable, '-c', 'import datetime; print("OK", end="")', capture_output=False
    )

    await asyncio.sleep(0.5)
    assert rule.ret.returncode == 0
    assert rule.ret.stdout is None
    assert rule.ret.stderr is None


@pytest.mark.no_internals
async def test_run_func_cancel(rule):
    task = rule.execute_subprocess(
        rule.set_ret, sys.executable, '-c', 'import time; time.sleep(5)', capture_output=False
    )

    await asyncio.sleep(0.2)
    task.cancel()
    await asyncio.sleep(0.1)
    assert rule.ret.returncode == -2
    assert rule.ret.stdout == 'Task cancelled'
    assert rule.ret.stderr == 'CancelledError'


@pytest.mark.no_internals
async def test_invalid_program(rule):
    rule.execute_subprocess(rule.set_ret, 'ProgramThatDoesNotExist', capture_output=True)

    await asyncio.sleep(0.5)
    assert rule.ret.returncode == -1
    assert rule.ret.stdout == 'Error during process handling!'
    assert isinstance(rule.ret.stderr, str)


@pytest.mark.no_internals
async def test_exec_python_file(rule):
    rule.execute_python(rule.set_ret, Path(__file__).with_name('__exec_python_file.py'), capture_output=True)

    await asyncio.sleep(0.5)
    assert rule.ret.stderr == ''
    assert rule.ret.returncode == 0
    assert loads(rule.ret.stdout)['cwd'] == str(Path(__file__).parent)


@pytest.mark.no_internals
async def test_exec_python_module(rule):
    folder = Path(__file__).parent
    rule.execute_python(rule.set_ret, '__exec_python_module', capture_output=True, additional_python_path=[folder])

    await asyncio.sleep(0.5)
    assert rule.ret.stderr == ''
    assert rule.ret.stdout == 'module ok'
    assert rule.ret.returncode == 0


@pytest.mark.no_internals
async def test_pythonpath(monkeypatch):
    folder = str(Path(__file__).parent)

    env = {}
    monkeypatch.setattr(rule_subprocess.os, 'environ', env)

    # Check set
    args, kwargs = rule_subprocess.build_exec_params(_additional_python_path=[folder])
    assert kwargs['env']['PYTHONPATH'] == folder

    # Check append
    env['PYTHONPATH'] = 'existing/folder'
    args, kwargs = rule_subprocess.build_exec_params(_additional_python_path=[folder])
    assert kwargs['env']['PYTHONPATH'].startswith(folder)
    assert kwargs['env']['PYTHONPATH'].endswith('existing/folder')

    # Check folder
    with pytest.raises(FileNotFoundError) as e:
        rule_subprocess.build_exec_params(_additional_python_path=[folder, 'asdf'])
    assert str(e.value) == 'Additional python path folder "asdf" does not exist!'
