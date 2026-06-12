import asyncio
import logging
from collections.abc import AsyncGenerator
from datetime import timedelta
from typing import Any
from unittest.mock import MagicMock, Mock

import pytest

from HABApp.core.events import ItemNoChangeEvent, ItemNoUpdateEvent
from HABApp.core.internals import EventBus
from HABApp.core.items import Item
from HABApp.core.lib import DebouncedCallRegistry
from HABApp.core.lib.asyncio.asyncio import AsyncioProvider
from HABApp.core.provider import HABAPP_PROVIDER
from tests.helpers import LogCollector
from tests.helpers.parent_rule import DummyRule


@pytest.fixture
async def registry() -> AsyncGenerator[DebouncedCallRegistry, Any]:
    r = DebouncedCallRegistry(AsyncioProvider())

    # ToDo: rework so we don't have to add it to HABAPP_PROVIDER
    if HABAPP_PROVIDER.has_factory(DebouncedCallRegistry):
        HABAPP_PROVIDER.remove_factory(DebouncedCallRegistry)
    HABAPP_PROVIDER.add_object(r, DebouncedCallRegistry)
    yield r
    HABAPP_PROVIDER._created.pop(DebouncedCallRegistry, None)
    await r.shutdown()


async def test_multiple_add(parent_rule: DummyRule, test_logs: LogCollector, registry) -> None:
    test_logs.set_min_level(logging.DEBUG)

    i = Item('test', event_bus=Mock(EventBus))
    w1 = i.watch_change(5)
    w2 = i.watch_change(5)

    f, = i._last_change._factories
    assert f._watchers == 2

    w1.cancel()
    assert f._watchers == 1

    w2.cancel()
    assert not i._last_change._factories

    assert test_logs.update().get_messages() == [
        '   [HABApp] | DEBUG | Created ItemNoChangeEvent(test, 5.0s)',
        '   [HABApp] | DEBUG | ItemNoChangeEvent(test, 5.0s) has now 1 watcher',
        '   [HABApp] | DEBUG | ItemNoChangeEvent(test, 5.0s) has now 2 watchers',
        '   [HABApp] | DEBUG | ItemNoChangeEvent(test, 5.0s) has now 1 watcher',
        '   [HABApp] | DEBUG | ItemNoChangeEvent(test, 5.0s) has now 0 watchers',
        '   [HABApp] | DEBUG | Removed ItemNoChangeEvent(test, 5.0s)',
    ]
    test_logs.caplog.clear()


@pytest.mark.parametrize('method', ('watch_update', 'watch_change'))
async def test_watch_update(parent_rule: DummyRule, sync_worker, caplog, method, registry) -> None:
    caplog.set_level(0)
    cb = MagicMock()
    cb.__name__ = 'MockName'

    secs = 0.2

    i = Item('test', event_bus=Mock(EventBus))
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
