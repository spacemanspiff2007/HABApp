from datetime import datetime
from unittest.mock import MagicMock

import asyncio
import pytest
import pytz

import HABApp
from HABApp.core.items.base_item import ChangedTime, UpdatedTime


@pytest.yield_fixture()
def event_loop():
    yield HABApp.core.const.loop


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
    assert w1.task.done()
    assert not w2.task.done()

    assert w2 in u.tasks
    w2.cancel()
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
