import asyncio
import logging
import time
from collections.abc import Generator
from time import monotonic
from types import TracebackType
from typing import Any, Final

from HABApp.core.items import BaseValueItem
from HABAppTests.compare_values import get_equal_text
from HABAppTests.errors import TestCaseFailed


log = logging.getLogger('HABApp.Tests')


class ItemWaiter:
    def __init__(self, item: str | BaseValueItem, timeout: float = 1) -> None:
        self._item: Final = item if not isinstance(item, str) else BaseValueItem.get_item(item)
        assert isinstance(self._item, BaseValueItem), f'{self._item} is not an Item'

        self._timeout: Final = timeout

    def _check_attribs(self, attribs: dict[str, Any]) -> Generator[float, Any, None]:
        start = monotonic()
        end = start + self._timeout

        while monotonic() < end:
            yield 0.01

            for name, target in attribs.items():
                if getattr(self._item, name) != target:
                    break
            else:
                return None

        indent = max(map(len, attribs))
        failed = [
            f'{name:>{indent:d}s}: {get_equal_text(getattr(self._item, name), target)}'
            for name, target in attribs.items()
        ]
        failed_msg = '\n'.join(failed)
        msg = f'Timeout waiting for {self._item.name}!\n{failed_msg}'
        raise TestCaseFailed(msg)

    def wait_for_attribs(self, **kwargs) -> None:
        for delay in self._check_attribs(kwargs):
            time.sleep(delay)

    async def async_wait_for_attribs(self, **kwargs) -> None:
        for delay in self._check_attribs(kwargs):
            await asyncio.sleep(delay)

    def wait_for_state(self, state=None) -> None:
        return self.wait_for_attribs(value=state)

    async def async_wait_for_state(self, state=None) -> None:
        return await self.async_wait_for_attribs(value=state)

    def __enter__(self) -> 'ItemWaiter':
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> bool:
        pass
