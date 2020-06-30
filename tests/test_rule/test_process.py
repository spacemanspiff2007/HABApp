import asyncio
import pytest
import sys

import HABApp
from HABApp.rule import Rule
from ..rule_runner import SimpleRuleRunner


@pytest.yield_fixture()
def event_loop():
    yield HABApp.core.const.loop


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


@pytest.mark.asyncio
async def test_run_func(rule):
    rule.execute_subprocess(
        rule.set_ret, sys.executable, '-c', 'import datetime; print("OK", end="")', capture_output=True
    )

    await asyncio.sleep(0.5)
    assert rule.ret.returncode == 0
    assert rule.ret.stdout == 'OK'
    assert rule.ret.stderr == ''


@pytest.mark.asyncio
async def test_run_func_no_cap(rule):
    rule.execute_subprocess(
        rule.set_ret, sys.executable, '-c', 'import datetime; print("OK", end="")', capture_output=False
    )

    await asyncio.sleep(0.5)
    assert rule.ret.returncode == 0
    assert rule.ret.stdout is None
    assert rule.ret.stderr is None


@pytest.mark.asyncio
async def test_invalid_program(rule):
    rule.execute_subprocess(rule.set_ret, 'ProgramThatDoesNotExist', capture_output=True)

    await asyncio.sleep(0.5)
    assert rule.ret.returncode == -1
    assert rule.ret.stdout is None
    assert isinstance(rule.ret.stderr, str)
