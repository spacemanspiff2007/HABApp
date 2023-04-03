from pendulum import datetime, duration
import pytest


START_TIME = datetime(2023, 4, 3, 8, 30)


@pytest.fixture
def runner():
    from HABApp.util.test.rule_runner import TimeAwareRuleRunner
    runner = TimeAwareRuleRunner(now=START_TIME)
    runner.set_up()
    yield runner
    runner.tear_down()


@pytest.mark.no_internals
def test_doc_run(runner):
    calls = []

    import HABApp

    class MyFirstRule(HABApp.Rule):
        def __init__(self, my_parameter):
            super().__init__()
            self.param = my_parameter
            self.run.soon(self.say_something)
            self.run.at(START_TIME + duration(seconds=30), self.say_something)

        def say_something(self):
            calls.append(self.param)

    # This is normal python code, so you can create Rule instances as you like
    for i in range(2):
        MyFirstRule(i)
    for t in ['Text 1', 'Text 2']:
        MyFirstRule(t)

    assert len(calls) == 0
    runner.process_events()
    assert len(calls) == 4
    runner.advance_time_by(duration(milliseconds=1))
    assert len(calls) == 4
    runner.advance_time_by(duration(seconds=30))
    assert len(calls) == 8
