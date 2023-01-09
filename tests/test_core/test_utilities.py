import asyncio

import pytest

from HABApp.core.lib import PendingFuture


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


async def test_pending_future_cancel():
    exception = None

    async def b():
        nonlocal exception
        try:
            await asyncio.sleep(200)
        except BaseException as e:
            exception = e

    p = PendingFuture(b, 0)
    p.reset()
    await asyncio.sleep(0.05)
    p.reset()
    await asyncio.sleep(0.05)
    p.cancel()

    assert exception is not None
    assert isinstance(exception, asyncio.CancelledError)
