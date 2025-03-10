import asyncio
from threading import Thread
from unittest.mock import Mock

import pytest

import HABApp
from HABApp.core import EventBus
from HABApp.core.asyncio import AsyncContextError, run_coro_from_thread, thread_context
from HABApp.core.wrapper import in_thread


async def test_error_msg() -> None:

    def my_sync_func():
        if thread_context.get(None) is None:
            raise AsyncContextError(my_sync_func)

    with pytest.raises(AsyncContextError) as e:
        my_sync_func()
    assert str(e.value) == 'Function "my_sync_func" may not be called from an async context!'

    thread_context.set('Test')
    my_sync_func()


async def run_in_thread(func: callable) -> None:
    t = Thread(target=func)
    t.start()
    while t.is_alive():
        await asyncio.sleep(0.1)
    t.join()


async def test_thread(caplog, eb: EventBus, monkeypatch) -> None:
    monkeypatch.setattr(HABApp.core, 'EventBus', eb)

    m = Mock()

    async def coro() -> None:
        m(1)

    def nothing():
        try:
            run_coro_from_thread(coro(), nothing)
        except Exception as e:
            print(e)
        return None

    m.assert_not_called()
    await run_in_thread(nothing)
    m.assert_called_once()

    logs = [msg.message for msg in caplog.get_records('call') if msg.levelname == 'ERROR']
    caplog.clear()

    assert len(eb.errors) == 1
    assert logs == eb.errors[0].splitlines()
    eb.errors.clear()

    assert logs[0] == 'Thread usage detected but no thread marker "@in_thread" was used!'
    assert logs[1] == 'See https://habapp.readthedocs.io/en/latest/troubleshooting.html for more information.'


async def test_thread_ok() -> None:
    m = Mock()

    async def coro() -> None:
        m(1)

    @in_thread
    def nothing():
        try:
            run_coro_from_thread(coro(), nothing)
        except Exception as e:
            print(e)
        return None

    m.assert_not_called()
    await run_in_thread(nothing)
    m.assert_called_once()
