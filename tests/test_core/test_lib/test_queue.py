import asyncio
from asyncio import QueueEmpty

import pytest

from HABApp.core.lib import SingleConsumerQueue


@pytest.fixture
async def queue() -> SingleConsumerQueue:
    return SingleConsumerQueue()


async def test_repr(queue: SingleConsumerQueue) -> None:
    assert repr(queue) == 'SingleConsumerQueue(is_open=True, queue_size=0)'

    queue.put_nowait('item')
    assert repr(queue) == 'SingleConsumerQueue(is_open=True, queue_size=1)'

    queue.set_open(False)
    assert repr(queue) == 'SingleConsumerQueue(is_open=False, queue_size=0)'


async def test_put_ignored_when_closed(queue: SingleConsumerQueue) -> None:
    queue.set_open(False)
    queue.put_nowait('a')
    with pytest.raises(QueueEmpty):
        queue.get_nowait()


async def test_put_get(queue: SingleConsumerQueue) -> None:
    values = ('first', 'second', 'third', 1, 2, 3)

    for value in values:
        queue.put_nowait(value)

    for value in values:
        assert queue.get_nowait() == value

    for value in values:
        queue.put_nowait(value)

    for value in values:
        assert await queue.get() == value


async def test_get_nowait_raises_on_empty(queue: SingleConsumerQueue) -> None:
    with pytest.raises(QueueEmpty):
        queue.get_nowait()


async def test_get_waits_for_item(queue: SingleConsumerQueue) -> None:
    async def producer() -> None:
        await asyncio.sleep(0.05)
        queue.put_nowait('delayed')

    t = asyncio.create_task(producer())
    assert await queue.get() == 'delayed'

    await t


async def test_multiple_consumers_error(queue: SingleConsumerQueue) -> None:
    task1 = asyncio.create_task(queue.get())
    await asyncio.sleep(0)  # let task1 start waiting

    task2 = asyncio.create_task(queue.get())
    with pytest.raises(RuntimeError, match='Only one consumer allowed'):
        await task2

    task1.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task1


async def test_set_open_clears(queue: SingleConsumerQueue) -> None:
    queue.put_nowait('a')
    queue.set_open(False)
    with pytest.raises(QueueEmpty):
        queue.get_nowait()


async def test_reopen_allows_new_items(queue: SingleConsumerQueue) -> None:
    queue.set_open(False)
    queue.put_nowait('ignored')
    queue.set_open(True)
    queue.put_nowait('visible')
    assert queue.get_nowait() == 'visible'


async def test_get_resumes_after_cancellation(queue: SingleConsumerQueue) -> None:

    # After a cancelled get(), a new get() must work correctly
    task = asyncio.create_task(queue.get())
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    queue.put_nowait('after_cancel')
    assert await queue.get() == 'after_cancel'


async def test_close_does_not_wake_waiting_consumer(queue: SingleConsumerQueue) -> None:

    task = asyncio.create_task(queue.get())
    await asyncio.sleep(0)

    queue.set_open(False)
    await asyncio.sleep(0)

    assert not task.done()  # still waiting

    queue.set_open(True)
    queue.put_nowait('visible')

    assert await task == 'visible'
