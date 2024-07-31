import asyncio
from unittest.mock import MagicMock

import pytest
from pendulum import UTC
from pendulum import now as pd_now

import HABApp
import HABApp.core.items.tmp_data
from HABApp.core.events import NoEventFilter
from HABApp.core.internals import EventBus, ItemRegistry, wrap_func
from HABApp.core.items import Item
from HABApp.core.items.base_item import ChangedTime, UpdatedTime
from tests.helpers import LogCollector, TestEventBus


@pytest.fixture(scope='function')
def u():
    a = UpdatedTime('test', pd_now(UTC))
    w1 = a.add_watch(1)
    w2 = a.add_watch(3)

    yield a

    # cancel the rest of the running tasks
    if w1._parent_ctx is not None:
        w1.cancel()
    if w2._parent_ctx is not None:
        w2.cancel()


@pytest.fixture(scope='function')
def c():
    a = ChangedTime('test', pd_now(UTC))
    w1 = a.add_watch(1)
    w2 = a.add_watch(3)

    yield a

    # cancel the rest of the running tasks
    if w1._parent_ctx is not None:
        w1.cancel()
    if w2._parent_ctx is not None:
        w2.cancel()


def test_sec_timedelta(parent_rule, test_logs: LogCollector):
    a = UpdatedTime('test', pd_now(UTC))
    w1 = a.add_watch(1)

    # We return the same object because it is the same time
    assert w1 is a.add_watch(1)
    assert w1 is a.add_watch(1.0)

    w2 = a.add_watch(3)
    assert w2.fut.secs == 3

    w1.cancel()
    w2.cancel()

    test_logs.add_expected('HABApp', 'WARNING', 'Watcher ItemNoUpdateWatch (1s) for test has already been created')


async def test_rem(parent_rule, u: UpdatedTime):
    for t in u.tasks:
        t.cancel()


async def test_cancel_running(parent_rule, u: UpdatedTime):
    u.set(pd_now(UTC))

    w1 = u.tasks[0]
    w2 = u.tasks[1]

    await asyncio.sleep(1.1)
    assert w1.fut.task.done()
    assert not w2.fut.task.done()

    assert w2 in u.tasks
    w2.cancel()
    await asyncio.sleep(0.05)
    u.set(pd_now(UTC))
    await asyncio.sleep(0.05)
    assert w2 not in u.tasks


async def test_event_update(parent_rule, u: UpdatedTime, sync_worker, eb: EventBus):
    m = MagicMock()
    u.set(pd_now(UTC))
    list = HABApp.core.internals.EventBusListener('test', wrap_func(m, name='MockFunc'), NoEventFilter())
    eb.add_listener(list)

    u.set(pd_now(UTC))
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


async def test_event_change(parent_rule, c: ChangedTime, sync_worker, eb: EventBus):
    m = MagicMock()
    c.set(pd_now(UTC))
    list = HABApp.core.internals.EventBusListener('test', wrap_func(m, name='MockFunc'), NoEventFilter())
    eb.add_listener(list)

    c.set(pd_now(UTC))
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
    await asyncio.sleep(0.01)


async def test_watcher_change_restore(parent_rule, ir: ItemRegistry):
    name = 'test_save_restore'

    item_a = Item(name)
    ir.add_item(item_a)
    watcher = item_a.watch_change(1)

    # remove item
    assert name not in HABApp.core.items.tmp_data.TMP_DATA
    ir.pop_item(name)
    assert name in HABApp.core.items.tmp_data.TMP_DATA

    item_b = Item(name)
    ir.add_item(item_b)

    assert item_b._last_change.tasks == [watcher]
    ir.pop_item(name)


async def test_watcher_update_restore(parent_rule, ir: ItemRegistry):
    name = 'test_save_restore'

    item_a = Item(name)
    ir.add_item(item_a)
    watcher = item_a.watch_update(1)

    # remove item
    assert name not in HABApp.core.items.tmp_data.TMP_DATA
    ir.pop_item(name)
    assert name in HABApp.core.items.tmp_data.TMP_DATA

    item_b = Item(name)
    ir.add_item(item_b)

    assert item_b._last_update.tasks == [watcher]
    ir.pop_item(name)


@pytest.mark.ignore_log_warnings()
async def test_watcher_update_cleanup(monkeypatch, parent_rule, c: ChangedTime,
                                      sync_worker, eb: TestEventBus, ir: ItemRegistry):
    monkeypatch.setattr(HABApp.core.items.tmp_data.CLEANUP, 'secs', 0.7)

    text_warning = ''

    def get_log(event):
        nonlocal text_warning
        text_warning = event

    eb.listen_events(HABApp.core.const.topics.TOPIC_WARNINGS, get_log, NoEventFilter())

    name = 'test_save_restore'
    item_a = HABApp.core.items.Item(name)
    ir.add_item(item_a)
    item_a.watch_update(1)

    # remove item
    assert name not in HABApp.core.items.tmp_data.TMP_DATA
    ir.pop_item(name)
    assert name in HABApp.core.items.tmp_data.TMP_DATA

    # ensure that the tmp data gets deleted
    await asyncio.sleep(0.8)
    assert name not in HABApp.core.items.tmp_data.TMP_DATA

    assert text_warning == 'Item test_save_restore has been deleted 0.7s ago even though it has item watchers.' \
                           ' If it will be added again the watchers have to be created again, too!'
