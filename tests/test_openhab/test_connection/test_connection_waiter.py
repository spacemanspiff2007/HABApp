import asyncio

import pytest

from HABApp.openhab.connection_handler.http_connection_waiter import WaitBetweenConnects

waited = -1


async def sleep(time):
    global waited
    waited = time


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
