import logging
import time
from types import TracebackType

from HABApp.core.items import BaseValueItem
from HABAppTests.compare_values import get_equal_text
from HABAppTests.errors import TestCaseFailed


log = logging.getLogger('HABApp.Tests')


class ItemWaiter:
    def __init__(self, item, timeout=1) -> None:
        self.item = item
        assert isinstance(item, BaseValueItem), f'{item} is not an Item'

        self.timeout = timeout

    def wait_for_attribs(self, **kwargs) -> bool:
        start = time.time()
        end = start + self.timeout

        while True:
            time.sleep(0.01)

            for name, target in kwargs.items():
                if getattr(self.item, name) != target:
                    break
            else:
                return True

            if time.time() > end:
                indent = max(map(len, kwargs))
                failed = [
                    f'{name:>{indent:d}s}: {get_equal_text(getattr(self.item, name), target)}'
                    for name, target in kwargs.items()
                ]
                failed_msg = '\n'.join(failed)
                msg = f'Timeout waiting for {self.item.name}!\n{failed_msg}'
                raise TestCaseFailed(msg)

    def wait_for_state(self, state=None):
        return self.wait_for_attribs(value=state)

    def __enter__(self) -> 'ItemWaiter':
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> bool:
        pass
