import asyncio
from datetime import date
from unittest.mock import AsyncMock, Mock

import pytest

import HABApp
from HABApp.core.const.topics import TOPIC_ERRORS
from HABApp.core.events import NoEventFilter
from HABApp.core.internals import EventBusListener, wrap_func
from HABApp.core.internals.wrapped_function.wrapped_sync import WrappedSyncFunction
from HABApp.core.internals.wrapped_function.wrapped_thread import (
    WrappedThreadFunction,
    create_thread_pool,
    stop_thread_pool,
)
from tests.helpers import TestEventBus


def test_error() -> None:
    with pytest.raises(TypeError) as e:
        wrap_func(None)
    assert str(e.value) == 'Callable or coroutine function expected! Got "None" (type NoneType)'

    with pytest.raises(TypeError) as e:
        wrap_func(6)
    assert str(e.value) == 'Callable or coroutine function expected! Got "6" (type int)'

    with pytest.raises(TypeError) as e:
        wrap_func(date(2023, 12, 24))
    assert str(e.value) == 'Callable or coroutine function expected! Got "2023-12-24" (type date)'


def test_sync_run(sync_worker) -> None:
    func = Mock()
    f = wrap_func(func, name='mock')
    f.run()
    func.assert_called_once_with()


async def test_async_run() -> None:
    coro = AsyncMock()
    f = wrap_func(coro, name='coro_mock')
    f.run()
    await asyncio.sleep(0.05)
    coro.assert_awaited_once()


def test_sync_args(sync_worker) -> None:
    func = Mock()
    f = wrap_func(func, name='mock')
    f.run('arg1', 'arg2', kw1='kw1')
    func.assert_called_once_with('arg1', 'arg2', kw1='kw1')


async def test_async_args() -> None:
    coro = AsyncMock()
    f = wrap_func(coro, name='coro_mock')
    f.run('arg1', 'arg2', kw1='kw1')

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

    f = wrap_func(func)
    err_func = AsyncMock()
    err_listener = EventBusListener(TOPIC_ERRORS, wrap_func(err_func, name='ErrMock'), NoEventFilter())
    eb.add_listener(err_listener)

    f.run()
    await asyncio.sleep(0.05)

    assert err_func.called
    err = err_func.call_args[0][0]
    assert isinstance(err, HABApp.core.events.habapp_events.HABAppException)
    assert err.func_name == name
    assert isinstance(err.exception, ZeroDivisionError)
    assert err.traceback.startswith('File ')


@pytest.fixture
def thread_pool():
    create_thread_pool(2)
    yield
    stop_thread_pool()


async def test_ret_wrapped_sync_func(thread_pool) -> None:

    def func() -> int:
        return 1

    ret = await WrappedSyncFunction(func).async_run()
    assert ret == 1

    ret = await WrappedThreadFunction(func).async_run()
    assert ret == 1


@pytest.mark.ignore_log_errors
async def test_wrapped_sync_func(thread_pool, eb: TestEventBus) -> None:
    eb.allow_errors = True

    def func() -> None:
        1/0

    ret = await WrappedThreadFunction(func).async_run()
    assert ret is None

    ret = await WrappedSyncFunction(func).async_run()
    assert ret is None
