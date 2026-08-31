import logging
import time
from typing import Final

from HABAppTests import OpenhabTmpItem, TestBaseRule
from whenever import Instant

from HABApp.openhab.items import StringItem


log: Final = logging.getLogger('Com.Rest')


class TestItemTimestamps(TestBaseRule):
    def __init__(self) -> None:
        super().__init__()
        self.add_test('test timestamps', self.test_timestamps)

    def test_timestamps(self) -> None:

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

                item_data = self.oh.get_item(item)

                if (last_state_update := item_data.last_state_update) is not None:
                    last_state_update = Instant.from_timestamp_millis(item_data.last_state_update).to_system_tz()
                if (last_state_change := item_data.last_state_change) is not None:
                    last_state_change = Instant.from_timestamp_millis(item_data.last_state_change).to_system_tz()

                log.debug(f' ITEM   last_state_update={last_state_update}, last_state_change={last_state_change}')

                assert send < item.last_update < receive
                if value != old_value:
                    assert send < item.last_change < receive

                time.sleep(9)


TestItemTimestamps()
