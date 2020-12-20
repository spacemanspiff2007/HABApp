import asyncio
from unittest.mock import MagicMock

import pytest

from HABApp.core.events import ItemNoUpdateEvent
from HABApp.core.items import Item
from tests.helpers.parent_rule import DummyRule
from ..helpers import TmpEventBus


@pytest.mark.asyncio
async def test_multiple_add(parent_rule: DummyRule):

    i = Item('test')
    w1 = i.watch_change(5)
    w2 = i.watch_change(5)

    assert w1 is w2

    w1.fut.cancel()
    w2 = i.watch_change(5)
    assert w1 is not w2


@pytest.mark.asyncio
async def test_watch(parent_rule: DummyRule, event_bus: TmpEventBus, sync_worker):

    cb = MagicMock()
    cb.__name__ = 'MockName'

    secs = 0.2

    i = Item('test')
    i.watch_update(secs / 2)
    w = i.watch_update(secs)
    w.listen_event(cb)

    i.post_value(1)
    await asyncio.sleep(0.3)

    cb.assert_called_once()
    assert isinstance(cb.call_args[0][0], ItemNoUpdateEvent)
    assert cb.call_args[0][0].name == 'test'
    assert cb.call_args[0][0].seconds == secs
