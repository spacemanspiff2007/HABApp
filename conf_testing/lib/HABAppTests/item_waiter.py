import logging
import time

import HABApp
from HABAppTests.compare_values import get_equal_text
from HABAppTests.errors import TestCaseFailed


log = logging.getLogger('HABApp.Tests')


class ItemWaiter:
    def __init__(self, item, timeout=1, item_compare: bool = True):
        self.item = item
        assert isinstance(item, HABApp.core.base.BaseValueItem), f'{item} is not an Item'

        self.timeout = timeout
        self.item_compare = item_compare

    def wait_for_state(self, state=None):

        start = time.time()
        end = start + self.timeout

        while True:
            time.sleep(0.01)
            if (self.item if self.item_compare else self.item.value) == state:
                return True

            if time.time() > end:
                raise TestCaseFailed(f'Timeout waiting for {self.item.name} {get_equal_text(state, self.item.value)}')

        raise ValueError()

    def __enter__(self) -> 'ItemWaiter':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
