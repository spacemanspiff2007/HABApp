import logging
from time import monotonic, sleep

from HABAppTests import TestBaseRule, get_random_name

from HABApp import Rule
from HABApp.core.events import ValueUpdateEventFilter
from HABApp.core.items import Item


log = logging.getLogger('HABApp.TestParameterFiles')


class TestSchedulerCallLive(Rule):
    """This rule is testing the Scheduler implementation"""

    def __init__(self) -> None:
        super().__init__()

        self.sunrise = self.run.at(self.run.trigger.sunrise(), print, 'sunrise')
        self.sunset = self.run.at(self.run.trigger.sunset(), print, 'sunset')

        self.run.soon(self.show_times)

    def show_times(self) -> None:
        print(f'Sunrise: {self.sunrise.get_next_run()}')
        print(f'Sunset : {self.sunset.get_next_run()}')


TestSchedulerCallLive()


class TestScheduler(TestBaseRule):
    """This rule is testing the Scheduler implementation"""

    def __init__(self) -> None:
        super().__init__()

        self.add_test('Test scheduler every', self.test_scheduler_every)

        self.run.at(self.run.trigger.sunrise(), print, 'sunrise')
        self.run.at(self.run.trigger.sunset(), print, 'sunset')

        self.item = Item.get_create_item(get_random_name('HABApp'))
        self.item.listen_event(lambda x: self.item_states.append(x), ValueUpdateEventFilter())
        self.item_states = []

    def test_scheduler_every(self) -> None:

        executions = 10
        calls = []

        def called() -> None:
            calls.append(monotonic())

        job = self.run.every(None, 0.5, called)
        job.to_item(self.item)

        try:
            started = monotonic()
            while monotonic() - started < executions * 0.6 + 1:
                sleep(0.1)

                if len(calls) >= executions:
                    break
        finally:
            job.cancel()

        assert len(calls) == executions, calls

        for i in range(len(calls) - 1):
            diff = calls[i + 1] - calls[i]
            assert 0.46 <= diff <= 0.54, diff

        sleep(0.1)
        assert len(self.item_states) == executions + 1  # First event before the first call, then None as the last event
        assert self.item_states[-1].value is None


TestScheduler()
