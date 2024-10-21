from datetime import timedelta
from time import sleep

from HABAppTests import OpenhabTmpItem, TestBaseRule

from HABApp.core.events import ValueUpdateEventFilter
from HABApp.core.items.base_valueitem import datetime
from HABApp.openhab.items import DatetimeItem


class TestSchedulerOhInteraction(TestBaseRule):
    def __init__(self) -> None:
        super().__init__()

        self.add_test('Test scheduler oh_item', self.test_scheduler_every)

    @OpenhabTmpItem.create('DateTime', arg_name='tmp_item')
    def test_scheduler_every(self, tmp_item: OpenhabTmpItem) -> None:

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

        assert item_states == [next_hour, None]


TestSchedulerOhInteraction()
