import asyncio
from unittest.mock import MagicMock
from datetime import timedelta

import pytest

from HABApp.core.events import ItemNoUpdateEvent, ItemNoChangeEvent
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
async def test_watch_update(parent_rule: DummyRule, event_bus: TmpEventBus, sync_worker, caplog):

    for meth in ('watch_update', 'watch_change'):

        cb = MagicMock()
        cb.__name__ = 'MockName'

        secs = 0.2

        i = Item('test')
        func = getattr(i, meth)
        func(secs / 2)
        w = func(timedelta(seconds=secs))
        w.listen_event(cb)

        i.post_value(1)
        await asyncio.sleep(0.3)

        cb.assert_called_once()
        assert isinstance(cb.call_args[0][0], ItemNoUpdateEvent if meth == 'watch_update' else ItemNoChangeEvent)
        assert cb.call_args[0][0].name == 'test'
        assert cb.call_args[0][0].seconds == secs
