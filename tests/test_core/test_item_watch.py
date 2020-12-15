from HABApp.core.items import Item
from tests.helpers.parent_rule import DummyRule
import pytest

@pytest.mark.asyncio
async def test_multiple_add(parent_rule: DummyRule):

    i = Item('test')
    w1 = i.watch_change(5)
    w2 = i.watch_change(5)

    assert w1 is w2

    w1.fut.cancel()
    w2 = i.watch_change(5)
    assert w1 is not w2
