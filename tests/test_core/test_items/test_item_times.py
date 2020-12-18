import asyncio
from datetime import datetime
from unittest.mock import MagicMock

import pytest
import pytz

import HABApp
import HABApp.core.items.tmp_data
from HABApp.core.items.base_item import ChangedTime, UpdatedTime
from ...helpers import TmpEventBus


@pytest.fixture(scope="function")
def u():
    a = UpdatedTime('test', datetime.now(tz=pytz.utc))
    w1 = a.add_watch(1)
    w2 = a.add_watch(3)

    yield a

    # cancel the rest of the running tasks
    w1.cancel()
    w2.cancel()


@pytest.fixture(scope="function")
def c():
    a = ChangedTime('test', datetime.now(tz=pytz.utc))
    w1 = a.add_watch(1)
    w2 = a.add_watch(3)

    yield a

    # cancel the rest of the running tasks
    w1.cancel()
    w2.cancel()


@pytest.mark.asyncio
async def test_rem(u: UpdatedTime):
    for t in u.tasks:
        t.cancel()


@pytest.mark.asyncio
async def test_cancel_running(u: UpdatedTime):
    u.set(datetime.now(tz=pytz.utc))

    w1 = u.tasks[0]
    w2 = u.tasks[1]

    await asyncio.sleep(1.1)
    assert w1.fut.task.done()
    assert not w2.fut.task.done()

    assert w2 in u.tasks
    w2.cancel()
    await asyncio.sleep(0.05)
    u.set(datetime.now(tz=pytz.utc))
    await asyncio.sleep(0.05)
    assert w2 not in u.tasks


@pytest.mark.asyncio
async def test_event_update(u: UpdatedTime):
    m = MagicMock()
    u.set(datetime.now(tz=pytz.utc))
    list = HABApp.core.EventBusListener('test', HABApp.core.WrappedFunction(m, name='MockFunc'))
    HABApp.core.EventBus.add_listener(list)

    u.set(datetime.now(tz=pytz.utc))
    await asyncio.sleep(1)
    m.assert_not_called()

    await asyncio.sleep(0.1)
    m.assert_called_once()

    c = m.call_args[0][0]
    assert isinstance(c, HABApp.core.events.ItemNoUpdateEvent)
    assert c.name == 'test'
    assert c.seconds == 1

    await asyncio.sleep(2)
    assert m.call_count == 2

    c = m.call_args[0][0]
    assert isinstance(c, HABApp.core.events.ItemNoUpdateEvent)
    assert c.name == 'test'
    assert c.seconds == 3

    list.cancel()


@pytest.mark.asyncio
async def test_event_change(c: ChangedTime):
    m = MagicMock()
    c.set(datetime.now(tz=pytz.utc))
    list = HABApp.core.EventBusListener('test', HABApp.core.WrappedFunction(m, name='MockFunc'))
    HABApp.core.EventBus.add_listener(list)

    c.set(datetime.now(tz=pytz.utc))
    await asyncio.sleep(1)
    m.assert_not_called()

    await asyncio.sleep(0.1)
    m.assert_called_once()

    c = m.call_args[0][0]
    assert isinstance(c, HABApp.core.events.ItemNoChangeEvent)
    assert c.name == 'test'
    assert c.seconds == 1

    await asyncio.sleep(2)
    assert m.call_count == 2

    c = m.call_args[0][0]
    assert isinstance(c, HABApp.core.events.ItemNoChangeEvent)
    assert c.name == 'test'
    assert c.seconds == 3

    list.cancel()


@pytest.mark.asyncio
async def test_watcher_change_restore(parent_rule):
    name = 'test_save_restore'

    item_a = HABApp.core.items.Item(name)
    HABApp.core.Items.add_item(item_a)
    watcher = item_a.watch_change(1)

    # remove item
    assert name not in HABApp.core.items.tmp_data.TMP_DATA
    HABApp.core.Items.pop_item(name)
    assert name in HABApp.core.items.tmp_data.TMP_DATA

    item_b = HABApp.core.items.Item(name)
    HABApp.core.Items.add_item(item_b)

    assert item_b._last_change.tasks == [watcher]
    HABApp.core.Items.pop_item(name)


@pytest.mark.asyncio
async def test_watcher_update_restore(parent_rule):
    name = 'test_save_restore'

    item_a = HABApp.core.items.Item(name)
    HABApp.core.Items.add_item(item_a)
    watcher = item_a.watch_update(1)

    # remove item
    assert name not in HABApp.core.items.tmp_data.TMP_DATA
    HABApp.core.Items.pop_item(name)
    assert name in HABApp.core.items.tmp_data.TMP_DATA

    item_b = HABApp.core.items.Item(name)
    HABApp.core.Items.add_item(item_b)

    assert item_b._last_update.tasks == [watcher]
    HABApp.core.Items.pop_item(name)


@pytest.mark.asyncio
async def test_watcher_update_cleanup(monkeypatch, parent_rule, c: ChangedTime, sync_worker, event_bus: TmpEventBus):
    monkeypatch.setattr(HABApp.core.items.tmp_data.CLEANUP, 'secs', 0.7)

    text_warning = ''

    def get_log(event):
        nonlocal text_warning
        text_warning = event

    event_bus.listen_events(HABApp.core.const.topics.WARNINGS, get_log)

    name = 'test_save_restore'
    item_a = HABApp.core.items.Item(name)
    HABApp.core.Items.add_item(item_a)
    item_a.watch_update(1)

    # remove item
    assert name not in HABApp.core.items.tmp_data.TMP_DATA
    HABApp.core.Items.pop_item(name)
    assert name in HABApp.core.items.tmp_data.TMP_DATA

    # ensure that the tmp data gets deleted
    await asyncio.sleep(0.8)
    assert name not in HABApp.core.items.tmp_data.TMP_DATA

    assert text_warning == 'Item test_save_restore has been deleted 0.7s ago even though it has item watchers.' \
                           ' If it will be added again the watchers have to be created again, too!'
