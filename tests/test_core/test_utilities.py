import asyncio

import pytest

import HABApp
from HABApp.core.const.utilities import PendingFuture


@pytest.yield_fixture()
def event_loop():
    yield HABApp.core.const.loop


@pytest.mark.asyncio
async def test_pending_future():
    a = 0

    async def b():
        nonlocal a
        a += 1

    p = PendingFuture(b, 0.01)
    for i in range(10):
        p.reset()
        await asyncio.sleep(0.05)
        assert i + 1 == a

    # let it run down once
    a = 0
    p = PendingFuture(b, 0.05)
    for i in range(10):
        p.reset()
        await asyncio.sleep(0.001)

    assert a == 0
    await asyncio.sleep(0.05)
    assert a == 1


@pytest.mark.asyncio
async def test_pending_future_cancel():
    exception = None

    async def b():
        nonlocal exception
        try:
            await asyncio.sleep(200)
        except Exception as e:
            exception = e

    p = PendingFuture(b, 0)
    p.reset()
    await asyncio.sleep(0.01)
    p.reset()
    await asyncio.sleep(0.01)
    assert isinstance(exception, asyncio.CancelledError)
    p.cancel()
