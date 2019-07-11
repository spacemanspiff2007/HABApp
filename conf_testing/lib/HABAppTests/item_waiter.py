import datetime
import logging
import time

import HABApp

log = logging.getLogger('HABApp.Tests')



class ItemWaiter:
    def __init__(self, item, timeout=1, item_compare: bool = True):
        self.item = item
        assert isinstance(item, HABApp.core.items.Item), f'{item} is not an Item'

        self.timeout = timeout
        self.item_compare = item_compare

        self.states_ok = True


    def wait_for_state(self, state=None):

        start = time.time()

        while True:
            time.sleep(0.01)
            if (self.item if self.item_compare else self.item.state) == state:
                return True

            if time.time() > start + self.timeout:
                self.states_ok = False
                log.error(f'Timeout waiting for state "{state}" for {self.item.name} ({self.item.__class__})! '
                          f'Current state: {self.item.state}')
                return False

        raise ValueError()

    def __enter__(self) -> 'ItemWaiter':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass