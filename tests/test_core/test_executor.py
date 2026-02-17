import asyncio
from collections.abc import AsyncGenerator
from datetime import date
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

import HABApp
from HABApp.config import ApplicationConfig
from HABApp.core.const.topics import TOPIC_ERRORS
from HABApp.core.events import NoEventFilter
from HABApp.core.internals import EventBusListener
from HABApp.core.internals.function_executor.factory import PoolExecutorFactory
from HABApp.core.internals.function_executor.thread_pool import HABAppThreadPool
from tests.helpers import TestEventBus


def test_error(sync_worker) -> None:
    with pytest.raises(TypeError) as e:
        sync_worker.create(None)
    assert str(e.value) == 'Callable or coroutine function expected! Got "None" (type NoneType)'

    with pytest.raises(TypeError) as e:
        sync_worker.create(6)
    assert str(e.value) == 'Callable or coroutine function expected! Got "6" (type int)'

    with pytest.raises(TypeError) as e:
        sync_worker.create(date(2023, 12, 24))
    assert str(e.value) == 'Callable or coroutine function expected! Got "2023-12-24" (type date)'


async def test_sync_run(sync_worker) -> None:
    func = Mock()
    f = sync_worker.create(func, name='mock')
    await f.execute()
    func.assert_called_once_with()


async def test_async_run(sync_worker) -> None:
    coro = AsyncMock()
    f = sync_worker.create(coro, name='coro_mock')
    await f.execute()
    await asyncio.sleep(0.05)
    coro.assert_awaited_once()


async def test_sync_args(sync_worker) -> None:
    func = Mock()
    f = sync_worker.create(func, name='mock')
    await f.execute('arg1', 'arg2', kw1='kw1')
    func.assert_called_once_with('arg1', 'arg2', kw1='kw1')


async def test_async_args(sync_worker) -> None:
    coro = AsyncMock()
    f = sync_worker.create(coro, name='coro_mock')
    await f.execute('arg1', 'arg2', kw1='kw1')

    await asyncio.sleep(0.05)
    coro.assert_awaited_once_with('arg1', 'arg2', kw1='kw1')


def func_div_error() -> None:
    1 / 0


async def async_func_div_error() -> None:
    1 / 0


@pytest.mark.ignore_log_errors
@pytest.mark.parametrize(
    'func, name', [(func_div_error, 'func_div_error'), (async_func_div_error, 'async_func_div_error')])
async def test_async_error_wrapper(eb: TestEventBus, name, func, sync_worker) -> None:
    eb.allow_errors = True

    f = sync_worker.create(func)
    err_func = AsyncMock()
    err_listener = EventBusListener(TOPIC_ERRORS, sync_worker.create(err_func, name='ErrMock'), NoEventFilter())
    eb.add_listener(err_listener)

    await f.execute()
    await asyncio.sleep(0.05)

    assert err_func.called
    err = err_func.call_args[0][0]
    assert isinstance(err, HABApp.core.events.habapp_events.HABAppException)
    assert err.func_name == name
    assert isinstance(err.exception, ZeroDivisionError)
    assert err.traceback.startswith('File ')


@pytest.fixture
async def thread_pool() -> AsyncGenerator[HABAppThreadPool, Any]:
    cfg = ApplicationConfig()
    cfg.habapp.thread_pool.threads = 2
    pool = HABAppThreadPool.create(cfg)
    yield pool
    await pool.shutdown()


@pytest.fixture
def executor_factory(eb, thread_pool) -> PoolExecutorFactory:
    return PoolExecutorFactory(eb, None, thread_pool)


async def test_ret_wrapped_sync_func(executor_factory: PoolExecutorFactory) -> None:

    def func() -> int:
        return 1

    ret = await executor_factory.create(func).execute()
    assert ret == 1

    ret = await executor_factory.create(func).execute()
    assert ret == 1


@pytest.mark.ignore_log_errors
async def test_wrapped_sync_func(
        executor_factory: PoolExecutorFactory, eb: TestEventBus) -> None:
    eb.allow_errors = True

    def func() -> None:
        1/0

    ret = await executor_factory.create(func).execute()
    assert ret is None

    ret = await executor_factory.create(func).execute()
    assert ret is None
