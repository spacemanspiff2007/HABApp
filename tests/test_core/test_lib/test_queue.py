import asyncio
import logging
from asyncio import QueueEmpty
from typing import Final

import pytest

from HABApp.core.lib import SingleConsumerQueue, WatchedSingleConsumerQueue


@pytest.fixture(params=(SingleConsumerQueue, WatchedSingleConsumerQueue))
async def queue(request) -> SingleConsumerQueue:
    cls = request.param
    return cls()


async def test_repr(queue: SingleConsumerQueue) -> None:
    cls_name = queue.__class__.__name__
    assert repr(queue) == f'{cls_name:s}(is_open=True, queue_size=0)'

    queue.put_nowait('item')
    assert repr(queue) == f'{cls_name:s}(is_open=True, queue_size=1)'

    queue.set_open(False)
    assert repr(queue) == f'{cls_name:s}(is_open=False, queue_size=0)'


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


# ---------------------------------------------------------------------------
# WatchedSingleConsumerQueue tests
# ---------------------------------------------------------------------------

class _SteppableSleep:
    """A controllable sleep replacement that lets tests advance the watcher one iteration at a time."""

    def __init__(self) -> None:
        self._proceed: Final = asyncio.Event()
        self._arrived: Final = asyncio.Event()

    async def __call__(self, _seconds: int) -> None:
        self._arrived.set()
        await self._proceed.wait()
        self._proceed.clear()
        self._arrived.clear()

    async def wait_until_sleeping(self) -> None:
        """Wait until the watcher is blocked inside sleep."""
        await self._arrived.wait()

    def step(self) -> None:
        """Release one sleep call so the watcher runs one check."""
        self._arrived.clear()
        self._proceed.set()


def _fill(q: WatchedSingleConsumerQueue, n: int) -> None:
    for i in range(n):
        q.put_nowait(i)


def _drain(q: WatchedSingleConsumerQueue, n: int) -> None:
    for _ in range(n):
        q.get_nowait()


async def _tick(task: asyncio.Task, sleeper: _SteppableSleep) -> None:
    """Advance the watcher by one iteration and wait until it sleeps again."""
    sleeper.step()
    await sleeper.wait_until_sleeping()
    assert not task.done(), 'watcher task exited unexpectedly'


@pytest.fixture
def log(caplog: pytest.LogCaptureFixture) -> logging.Logger:
    logger = logging.getLogger('test.watched_queue')
    logger.setLevel(logging.DEBUG)
    return logger


async def test_watcher_no_log_when_below_threshold(log: logging.Logger, caplog: pytest.LogCaptureFixture) -> None:
    sleeper = _SteppableSleep()
    q = WatchedSingleConsumerQueue()
    task = asyncio.create_task(q.queue_watcher_task(log, 'test', sleep=sleeper, first_msg_at=10))

    await sleeper.wait_until_sleeping()

    # fill to exactly threshold — should not trigger
    _fill(q, 10)
    assert len(q) == 10

    await _tick(task, sleeper)
    assert caplog.records == []

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


async def test_watcher_warns_above_threshold(log: logging.Logger, caplog: pytest.LogCaptureFixture) -> None:
    sleeper = _SteppableSleep()
    q = WatchedSingleConsumerQueue()
    task = asyncio.create_task(q.queue_watcher_task(log, 'test', sleep=sleeper, first_msg_at=10))

    await sleeper.wait_until_sleeping()

    _fill(q, 11)

    await _tick(task, sleeper)

    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.WARNING
    assert caplog.records[0].message == '11 messages in test queue'
    caplog.clear()

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


async def test_watcher_escalating_warnings(log: logging.Logger, caplog: pytest.LogCaptureFixture) -> None:
    """After a warning at size 11 (upper becomes 22), adding more items up to 22 should not warn again,
    but exceeding 22 should produce a second warning."""
    sleeper = _SteppableSleep()
    q = WatchedSingleConsumerQueue()
    task = asyncio.create_task(q.queue_watcher_task(log, 'test', sleep=sleeper, first_msg_at=10))

    await sleeper.wait_until_sleeping()

    # first warning: 11 items -> upper becomes 22, lower becomes 5
    _fill(q, 11)
    await _tick(task, sleeper)
    assert len(caplog.records) == 1
    caplog.clear()

    # 20 items total (still <= 22) — no new warning
    _fill(q, 9)
    await _tick(task, sleeper)
    assert caplog.records == []

    # 25 items total (> 22) — second warning; upper becomes 50, lower becomes 12
    _fill(q, 5)
    assert len(q) == 25
    await _tick(task, sleeper)
    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.WARNING
    assert caplog.records[0].message == '25 messages in test queue'
    caplog.clear()

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


async def test_watcher_recovery_partial(log: logging.Logger, caplog: pytest.LogCaptureFixture) -> None:
    """When the queue drops below lower but lower > last_info_at, an info with the count is logged."""
    sleeper = _SteppableSleep()
    # first_msg_at=10 -> last_info_at=5
    q = WatchedSingleConsumerQueue()
    task = asyncio.create_task(q.queue_watcher_task(log, 'test', sleep=sleeper, first_msg_at=10))

    await sleeper.wait_until_sleeping()

    # Trigger a large warning to get a high lower bound:
    # size 200 > upper(10) -> upper=400, lower=100
    _fill(q, 200)
    with caplog.at_level(logging.DEBUG):
        await _tick(task, sleeper)
    assert caplog.records[-1].levelno == logging.WARNING
    caplog.clear()

    # Drain to 50 (< lower=100) ->
    #   upper = max(50//2, 10) = 25, lower = 50//2 = 25
    #   25 > last_info_at(5) -> log info with count, NOT "queue OK"
    _drain(q, 150)
    assert len(q) == 50
    await _tick(task, sleeper)

    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.INFO
    assert caplog.records[0].message == '50 messages in test queue'

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


async def test_watcher_recovery_full(log: logging.Logger, caplog: pytest.LogCaptureFixture) -> None:
    """When the queue fully drains, lower drops to <= last_info_at and 'queue OK' is logged."""
    sleeper = _SteppableSleep()
    # first_msg_at=10 -> last_info_at=5
    q = WatchedSingleConsumerQueue()
    task = asyncio.create_task(q.queue_watcher_task(log, 'test', sleep=sleeper, first_msg_at=10))

    await sleeper.wait_until_sleeping()

    # Trigger warning: 11 items -> upper=22, lower=5
    _fill(q, 11)
    with caplog.at_level(logging.DEBUG):
        await _tick(task, sleeper)
    caplog.clear()

    # Drain to 2 (< lower=5) ->
    #   upper = max(2//2, 10) = 10, lower = 2//2 = 1
    #   1 <= last_info_at(5) -> lower=-1, log "queue OK"
    _drain(q, 9)
    assert len(q) == 2
    await _tick(task, sleeper)

    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.INFO
    assert caplog.records[0].message == 'test queue OK'
    caplog.clear()

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


async def test_watcher_full_cycle(log: logging.Logger, caplog: pytest.LogCaptureFixture) -> None:
    """After full recovery (lower=-1), a new spike should trigger a fresh warning."""
    sleeper = _SteppableSleep()
    q = WatchedSingleConsumerQueue()
    task = asyncio.create_task(q.queue_watcher_task(log, 'test', sleep=sleeper, first_msg_at=10))

    await sleeper.wait_until_sleeping()

    with caplog.at_level(logging.DEBUG):
        # 1. Spike → warning
        _fill(q, 15)
        await _tick(task, sleeper)
        assert caplog.records[-1].levelno == logging.WARNING
        caplog.clear()

        # 2. Full drain → "queue OK"
        _drain(q, 15)
        assert len(q) == 0
        await _tick(task, sleeper)
        assert caplog.records[-1].message == 'test queue OK'
        caplog.clear()

        # 3. No messages when idle
        await _tick(task, sleeper)
        assert caplog.records == []

        # 4. New spike → fresh warning again (threshold is reset)
        _fill(q, 12)
        await _tick(task, sleeper)
        assert len(caplog.records) == 1
        assert caplog.records[0].levelno == logging.WARNING
        caplog.clear()

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


async def test_watcher_empty_queue_no_log(log: logging.Logger, caplog: pytest.LogCaptureFixture) -> None:
    """An empty queue produces no log messages even over many iterations."""
    sleeper = _SteppableSleep()
    q = WatchedSingleConsumerQueue()
    task = asyncio.create_task(q.queue_watcher_task(log, 'test', sleep=sleeper, first_msg_at=10))

    await sleeper.wait_until_sleeping()

    with caplog.at_level(logging.DEBUG):
        for _ in range(100):
            await _tick(task, sleeper)
        assert caplog.records == []

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
