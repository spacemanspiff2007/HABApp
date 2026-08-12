import time

from HABAppTests import OpenhabTmpItem, TestBaseRule
from whenever import Instant

from HABApp.openhab.items import StringItem


class TestItemTimestamps(TestBaseRule):
    def __init__(self) -> None:
        super().__init__()
        self.add_test('test timestamps', self.test_timestamps)

    def test_timestamps(self) -> bool:

        with OpenhabTmpItem('String') as tmp_item:
            item = StringItem.get_item(tmp_item.name)

            item.oh_post_update('a')
            time.sleep(10)

            for value in ('b', 'c', 'c'):

                old_value = item.value

                send = Instant.now()
                receive = send.add(seconds=0.5)
                item.oh_post_update(value)

                # wait for the event to arrive
                time.sleep(1)

                assert send < item.last_update < receive
                if value != old_value:
                    assert send < item.last_change < receive

                time.sleep(9)


TestItemTimestamps()
