import logging
import time

from HABAppTests import TestBaseRule
from HABAppTests.errors import TestCaseFailed

from HABApp.core.events import ValueUpdateEventFilter
from HABApp.core.items import Item
from HABApp.util import EventListenerGroup


log = logging.getLogger('HABApp.Tests.MultiMode')


class TestListenerGroup(TestBaseRule):
    """This rule is testing the Parameter implementation"""

    def __init__(self) -> None:
        super().__init__()

        self.my_item1 = Item.get_create_item('EventGroupItem_1')
        self.my_item2 = Item.get_create_item('EventGroupItem_2')

        self.grp = EventListenerGroup().add_listener(
            [self.my_item1, self.my_item2], self.__callback, ValueUpdateEventFilter())

        self.add_test('Test EventListenerGroup', self.test_basic)
        self.add_test('Test EventListenerGroup deactivate', self.test_deactivate)

        self.calls = []

    def __callback(self, event) -> None:
        self.calls.append(event)

    def wait_for_cb(self, expected_len: int, min_time=None):
        start = time.time()
        while True:
            dur = time.time() - start
            if len(self.calls) == expected_len:
                if min_time is None:
                    break
                if dur > min_time:
                    break
            if dur > 1:
                raise TestCaseFailed('Timeout while waiting for calls!')
            time.sleep(0.01)

    def test_basic(self) -> None:
        self.calls.clear()
        self.grp.listen()

        self.my_item2.post_value(1)

        self.wait_for_cb(1)
        assert self.calls[0].value == 1
        assert self.calls[0].name == self.my_item2.name

        # Cancel
        self.grp.cancel()

        self.wait_for_cb(1, min_time=0.1)
        self.my_item1.post_value(5)
        self.my_item2.post_value(6)

        self.wait_for_cb(1, min_time=0.1)
        assert self.calls[0].value == 1
        assert self.calls[0].name == self.my_item2.name

    def test_deactivate(self) -> None:
        self.calls.clear()
        self.grp.listen()

        # deactivate listener
        assert self.grp.deactivate_listener(self.my_item2.name)

        self.my_item2.post_value(1)
        self.my_item1.post_value(2)

        self.wait_for_cb(1, min_time=0.1)
        assert self.calls[0].value == 2
        assert self.calls[0].name == self.my_item1.name

        # activate listener
        assert self.grp.activate_listener(self.my_item2.name)

        self.my_item2.post_value(5)
        self.my_item1.post_value(6)

        self.wait_for_cb(3, min_time=0.1)
        assert self.calls[0].value == 2
        assert self.calls[0].name == self.my_item1.name
        assert self.calls[1].value == 5
        assert self.calls[1].name == self.my_item2.name
        assert self.calls[2].value == 6
        assert self.calls[2].name == self.my_item1.name

        # Cancel
        self.grp.cancel()


TestListenerGroup()
