import asyncio
from datetime import timedelta
from unittest.mock import MagicMock

import pytest

from HABApp.core.events import ItemNoUpdateEvent, ItemNoChangeEvent
from HABApp.core.items import Item
from tests.helpers import LogCollector
from tests.helpers.parent_rule import DummyRule


async def test_multiple_add(parent_rule: DummyRule, test_logs: LogCollector):

    i = Item('test')
    w1 = i.watch_change(5)
    w2 = i.watch_change(5)

    assert w1 is w2
    w1.fut.cancel()

    w2 = i.watch_change(5)
    assert w1 is not w2
    w2.fut.cancel()

    test_logs.add_ignored('HABApp', 'WARNING', 'Watcher ItemNoChangeWatch (5s) for test has already been created')


@pytest.mark.parametrize('method', ('watch_update', 'watch_change'))
async def test_watch_update(parent_rule: DummyRule, sync_worker, caplog, method):
    caplog.set_level(0)
    cb = MagicMock()
    cb.__name__ = 'MockName'

    secs = 0.2

    i = Item('test')
    func = getattr(i, method)
    func(secs / 2)
    w = func(timedelta(seconds=secs))
    w.listen_event(cb)

    i.post_value(1)
    await asyncio.sleep(0.3)

    for c in caplog.records:
        print(c)

    cb.assert_called_once()
    assert isinstance(cb.call_args[0][0], ItemNoUpdateEvent if method == 'watch_update' else ItemNoChangeEvent)
    assert cb.call_args[0][0].name == 'test'
    assert cb.call_args[0][0].seconds == secs
