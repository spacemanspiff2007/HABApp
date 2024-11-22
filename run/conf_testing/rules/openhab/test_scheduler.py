from datetime import timedelta
from time import monotonic, sleep

from HABAppTests import OpenhabTmpItem, TestBaseRule

from HABApp.core.events import ValueUpdateEventFilter
from HABApp.core.items.base_valueitem import datetime
from HABApp.openhab.items import DatetimeItem


class TestSchedulerOhInteraction(TestBaseRule):
    def __init__(self) -> None:
        super().__init__()

        self.add_test('Test scheduler oh_item once', self.test_scheduler_once)
        self.add_test('Test scheduler oh_item every', self.test_scheduler_every)
        self.add_test('Test scheduler oh_item countdown', self.test_scheduler_countdown, cb_async=False)
        self.add_test('Test scheduler oh_item countdown async', self.test_scheduler_countdown, cb_async=True)

    @OpenhabTmpItem.create('DateTime', arg_name='tmp_item')
    def test_scheduler_once(self, tmp_item: OpenhabTmpItem) -> None:

        item_states = []
        item = DatetimeItem.get_item(tmp_item.name)
        listener = item.listen_event(lambda x: item_states.append(x), ValueUpdateEventFilter())

        next_hour = datetime.now().replace(second=0, microsecond=0) + timedelta(hours=1)

        try:
            job = self.run.once(next_hour, lambda: 1/0)
            job.to_item(item)
            job.cancel()
            sleep(0.2)
        finally:
            listener.cancel()

        assert [v.value for v in item_states] == [next_hour, None]

    @OpenhabTmpItem.create('DateTime', arg_name='tmp_item')
    def test_scheduler_every(self, tmp_item: OpenhabTmpItem) -> None:

        item_states = []
        item = DatetimeItem.get_item(tmp_item.name)
        listener = item.listen_event(lambda x: item_states.append(x), ValueUpdateEventFilter())

        next_hour = datetime.now().replace(second=0, microsecond=0) + timedelta(hours=1)

        try:
            job = self.run.at(self.run.trigger.interval(next_hour, 7200), lambda: 1/0)
            job.to_item(item)
            job.pause()
            job.resume()
            job.cancel()
            sleep(0.2)
        finally:
            listener.cancel()

        assert [v.value for v in item_states] == [next_hour, None, next_hour, None]

    @OpenhabTmpItem.create('DateTime', arg_name='tmp_item')
    def test_scheduler_countdown(self, tmp_item: OpenhabTmpItem, cb_async: bool) -> None:

        calls = []
        item_states = []

        item = DatetimeItem.get_item(tmp_item.name)
        listener = item.listen_event(lambda x: item_states.append(x.value), ValueUpdateEventFilter())

        def reset_func() -> None:
            calls.append(monotonic())
            job.reset()

        async def async_reset_func() -> None:
            reset_func()

        start = monotonic()
        runs = 3
        try:
            job = self.run.countdown(1, reset_func if not cb_async else async_reset_func)
            job.to_item(item)
            job.reset()
            sleep(runs + 0.3)
            job.cancel()
            sleep(0.2)
        finally:
            listener.cancel()

        assert len(item_states) == 2 + 2 * runs + 1
        for obj in item_states[::2]:
            assert obj is None
        for obj in item_states[1::2]:
            assert obj is not None

        assert len(calls) == runs
        for i, ts in enumerate(calls):
            assert 0.75 <= (ts - start) - i <= 1.15, (ts - start) - i


TestSchedulerOhInteraction()
