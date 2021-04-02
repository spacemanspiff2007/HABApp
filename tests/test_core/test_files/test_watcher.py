import asyncio
from pathlib import Path
from unittest.mock import Mock

import pytest
from watchdog.events import FileSystemEvent

import HABApp.core.files.watcher.file_watcher
from HABApp.core.files.watcher import AggregatingAsyncEventHandler
from ...helpers import TmpEventBus


@pytest.mark.asyncio
async def test_file_events(monkeypatch, event_bus: TmpEventBus, sync_worker):
    
    wait_time = 0.1
    monkeypatch.setattr(HABApp.core.files.watcher.file_watcher, 'DEBOUNCE_TIME', wait_time)
    
    m = Mock()
    handler = AggregatingAsyncEventHandler(Path('folder'), m, '.tmp', False)
    
    async def generate_events(count: int, name: str, sleep: float):
        for _ in range(count):
            handler.dispatch(FileSystemEvent(name))
            await asyncio.sleep(sleep)
        
    await asyncio.gather(
        generate_events(3, 'test/t1.tmp', wait_time),
        generate_events(9, 'test/t2.tmp', wait_time / 2),
        generate_events(18, 'test/t3.tmp', wait_time / 5),
    )

    await asyncio.sleep(wait_time + 0.01)
    
    m.assert_called_once()
    assert set(*m.call_args[0]) == {Path('test/t1.tmp'), Path('test/t2.tmp'), Path('test/t3.tmp')}
