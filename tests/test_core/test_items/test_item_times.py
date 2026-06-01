import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import MagicMock, Mock

import pytest
from whenever import Instant, TimeDelta

import HABApp
from HABApp.core.events import NoEventFilter
from HABApp.core.internals import EventBus, ItemRegistry
from HABApp.core.items import Item
from HABApp.core.items.base_item_times import ItemChangeTime, ItemTimeWatch, ItemUpdateTime
from HABApp.core.items.base_item_times_data import ItemTimesBackup
from HABApp.core.lib import DebouncedCallRegistry
from HABApp.core.provider import HABAPP_PROVIDER
from tests.helpers import TestEventBus


@pytest.fixture
def update_time_1() -> Generator[tuple[ItemUpdateTime, ItemTimeWatch, ItemTimeWatch], Any, None]:
    a = ItemUpdateTime(Instant.now())
    w1 = a.add_watch('test', 1)
    w2 = a.add_watch('test', 3)

    yield a, w1, w2

    # cancel the rest of the running tasks
    if w1._parent_ctx is not None:
        w1.cancel()
    if w2._parent_ctx is not None:
        w2.cancel()


@pytest.fixture
def update_time_2() -> Generator[tuple[ItemChangeTime, ItemTimeWatch, ItemTimeWatch], Any, None]:
    a = ItemChangeTime(Instant.now())
    w1 = a.add_watch('test', 1)
    w2 = a.add_watch('test', 3)

    yield a, w1, w2

    # cancel the rest of the running tasks
    if w1._parent_ctx is not None:
        w1.cancel()
    if w2._parent_ctx is not None:
        w2.cancel()


@pytest.fixture(autouse=True)
async def registry() -> AsyncGenerator[DebouncedCallRegistry, Any]:
    r = DebouncedCallRegistry()

    # ToDo: rework so we don't have to add it to HABAPP_PROVIDER
    if HABAPP_PROVIDER.has_factory(DebouncedCallRegistry):
        HABAPP_PROVIDER.remove_factory(DebouncedCallRegistry)
    HABAPP_PROVIDER.add_object(r, DebouncedCallRegistry)
    yield r
    HABAPP_PROVIDER._created.pop(DebouncedCallRegistry, None)
    await r.shutdown()


@pytest.fixture
def item_times_backup(registry) -> Generator[ItemTimesBackup, Any, None]:
    b = ItemTimesBackup(registry)
    if HABAPP_PROVIDER.has_factory(ItemTimesBackup):
        HABAPP_PROVIDER.remove_factory(ItemTimesBackup)
    HABAPP_PROVIDER.add_object(b, ItemTimesBackup)
    yield b
    HABAPP_PROVIDER._created.pop(ItemTimesBackup, None)


async def test_cancel_running(parent_rule, update_time_1) -> None:
    u, w1, w2 = update_time_1

    now = Instant.now()
    u.set(now)

    await asyncio.sleep(0.05)

    f1, f2 = u._factories

    w2.cancel()
    await asyncio.sleep(0.05)

    f1, = u._factories


async def test_event_update(parent_rule, update_time_1: ItemUpdateTime, sync_worker, eb: EventBus) -> None:
    u, w1, w2 = update_time_1

    m = MagicMock()
    u.set(Instant.now())
    listener = HABApp.core.internals.EventBusListener('test', sync_worker.create(m, name='MockFunc'), NoEventFilter())
    eb.add_listener(listener)

    u.set(Instant.now())
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

    listener.cancel()


async def test_event_change(parent_rule, update_time_2: ItemChangeTime, sync_worker, eb: EventBus) -> None:
    u, w1, w2 = update_time_2

    m = MagicMock()
    u.set(Instant.now())
    listener = HABApp.core.internals.EventBusListener('test', sync_worker.create(m, name='MockFunc'), NoEventFilter())
    eb.add_listener(listener)

    u.set(Instant.now())
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

    listener.cancel()
    await asyncio.sleep(0.01)


@pytest.mark.parametrize(
    ('func_name', 'obj_name'), (('watch_change', '_last_change'), ('watch_update', '_last_update'), )
)
async def test_watcher_restore(func_name, obj_name,
                               parent_rule, ir: ItemRegistry, item_times_backup: ItemTimesBackup) -> None:

    name = 'test_save_restore'

    item_a = Item(name, event_bus=Mock(EventBus))
    ir.add_item(item_a)

    # calls item_a.watch_change(1)
    watcher = getattr(item_a, func_name)(1)

    # remove item
    assert name not in item_times_backup._data
    ir.pop_item(name)
    assert name in item_times_backup._data

    # adding restores the watcher
    item_b = Item(name, event_bus=Mock(EventBus))
    ir.add_item(item_b)

    assert getattr(item_b, obj_name)._factories == (watcher._event_factory, )


@pytest.mark.ignore_log_warnings
async def test_watcher_update_cleanup(
        parent_rule, update_time_2: ItemChangeTime, eb: TestEventBus, ir: ItemRegistry,
        item_times_backup: ItemTimesBackup) -> None:

    item_times_backup._timeout = TimeDelta(seconds=0.7)

    text_warning: str = ''

    def get_log(event: str) -> None:
        nonlocal text_warning
        text_warning += event

    eb.listen_events(HABApp.core.const.topics.TOPIC_WARNINGS, get_log, NoEventFilter())

    name = 'test_save_restore'
    item_a = Item(name, event_bus=Mock(EventBus))
    ir.add_item(item_a)
    item_a.watch_update(1)
    await asyncio.sleep(0.01)

    ir.pop_item(name)

    # ensure that the tmp data gets deleted
    await asyncio.sleep(0.8)

    assert text_warning == (
        'Item test_save_restore has been deleted 0h ago even though it has item watchers. '
        'If it will be added again the watchers have to be created again, too!'
    )
