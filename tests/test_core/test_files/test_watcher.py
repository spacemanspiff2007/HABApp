import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import Mock

import pytest
from watchdog.events import FileSystemEvent

import HABApp.core.files.watcher.file_watcher
from HABApp.core.files.watcher import AggregatingAsyncEventHandler
from HABApp.core.files.watcher.base_watcher import FileEndingFilter


@pytest.mark.asyncio
async def test_file_events(monkeypatch, sync_worker):

    wait_time = 0.1
    monkeypatch.setattr(HABApp.core.files.watcher.file_watcher, 'DEBOUNCE_TIME', wait_time)

    m = Mock()
    handler = AggregatingAsyncEventHandler(Path('folder'), m, FileEndingFilter('.tmp'), False)

    loop = asyncio.get_event_loop()

    ex = ThreadPoolExecutor(4)

    def generate_events(count: int, name: str, sleep: float):
        for _ in range(count):
            handler.dispatch(FileSystemEvent(name))
            time.sleep(sleep)

    await asyncio.gather(
        loop.run_in_executor(ex, generate_events, 3, 'test/t1.tmp', wait_time),
        loop.run_in_executor(ex, generate_events, 9, 'test/t2.tmp', wait_time / 2),
        loop.run_in_executor(ex, generate_events, 18, 'test/t3.tmp', wait_time / 5),
    )
    ex.shutdown()
    await asyncio.sleep(wait_time + 0.01)

    m.assert_called_once()
    assert set(*m.call_args[0]) == {Path('test/t1.tmp'), Path('test/t2.tmp'), Path('test/t3.tmp')}
