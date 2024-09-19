import subprocess
import sys

import pytest

import HABApp.core.lib.exceptions.format


@pytest.mark.no_internals
def test_doc_run():
    code = '''
calls = []

from tests import SimpleRuleRunner
runner = SimpleRuleRunner()
runner.set_up()
import HABApp

class MyFirstRule(HABApp.Rule):
    def __init__(self, my_parameter):
        super().__init__()
        self.param = my_parameter
        self.run.soon(self.say_something)

    def say_something(self):
        calls.append(self.param)

# This is normal python code, so you can create Rule instances as you like
for i in range(2):
    MyFirstRule(i)
for t in ['Text 1', 'Text 2']:
    MyFirstRule(t)
runner.process_events()
runner.tear_down()

assert len(calls) == 4
'''

    proc = subprocess.Popen(  # noqa: S603
        [sys.executable, '-c', code.encode('utf-8')],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    err = 1

    try:
        stdout, stderr = proc.communicate(timeout=5)
        err = 0
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()

    if err:
        print('')
        print('Standard Output:', stdout)
        print('Standard Error:', stderr)
        pytest.fail('Error')


@pytest.mark.no_internals()
def test_doc_run_exception(monkeypatch):
    """Check that the RuleRunner propagates exceptions which happen during exception formatting"""

    class MyException(Exception):
        pass

    def err(*args, **kwargs):
        raise MyException()

    monkeypatch.setattr(HABApp.core.lib.exceptions.format, 'format_frame_info', err)

    from tests import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()

    class MyFirstRule(HABApp.Rule):
        def __init__(self):
            super().__init__()
            self.run.soon(self.say_something)

        def say_something(self):
            1 / 0

    MyFirstRule()

    with pytest.raises(MyException):
        runner.process_events()
    runner.tear_down()
