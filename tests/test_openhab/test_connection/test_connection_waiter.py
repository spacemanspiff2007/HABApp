import asyncio
import pytest

import HABApp
from HABApp.openhab.connection_handler.http_connection_waiter import WaitBetweenConnects


@pytest.yield_fixture()
def event_loop():
    HABApp.core.WrappedFunction._EVENT_LOOP = HABApp.core.const.loop
    yield HABApp.core.const.loop


waited = -1


async def sleep(time):
    global waited
    waited = time


@pytest.mark.asyncio
async def test_aggregation_item(monkeypatch):
    monkeypatch.setattr(asyncio, "sleep", sleep)

    c = WaitBetweenConnects()

    await c.wait()
    assert waited == 0

    await c.wait()
    assert waited == 1

    await c.wait()
    assert waited == 2

    await c.wait()
    assert waited == 4

    await c.wait()
    assert waited == 8

    await c.wait()
    assert waited == 16

    await c.wait()
    assert waited == 32

    await c.wait()
    assert waited == 40

    await c.wait()
    assert waited == 48
