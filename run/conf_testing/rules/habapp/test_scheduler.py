import logging
import time

from HABAppTests import TestBaseRule, get_random_name

from HABApp.core.events import ValueUpdateEventFilter
from HABApp.core.items import Item


log = logging.getLogger('HABApp.TestParameterFiles')


class TestScheduler(TestBaseRule):
    """This rule is testing the Scheduler implementation"""

    def __init__(self):
        super().__init__()

        self.add_test('Test scheduler every', self.test_scheduler_every)

        f = self.run.on_sunrise(print, 'sunrise')
        print(f'Sunrise: {f.get_next_run()}')

        f = self.run.on_sunset(print, 'sunset')
        print(f'Sunset : {f.get_next_run()}')

        self.item = Item.get_create_item(get_random_name('HABApp'))
        self.item.listen_event(lambda x: self.item_states.append(x), ValueUpdateEventFilter())
        self.item_states = []

    def test_scheduler_every(self):

        executions = 5
        calls = []

        def called():
            calls.append(time.time())

        job = self.run.every(None, 0.5, called)
        job.to_item(self.item)

        try:
            started = time.time()
            while time.time() - started < 7:
                time.sleep(0.1)

                if len(calls) >= executions:
                    break

            assert len(calls) >= executions, calls

            for i in range(len(calls) - 1):
                diff = calls[i + 1] - calls[i]
                assert 0.47 <= diff <= 0.53, diff

        finally:
            job.cancel()

        assert len(self.item_states) == 6


TestScheduler()
