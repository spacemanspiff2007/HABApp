import asyncio
from datetime import date
from unittest.mock import AsyncMock, Mock

import pytest

import HABApp
from HABApp.core.const.topics import TOPIC_ERRORS as TOPIC_ERRORS
from HABApp.core.events import NoEventFilter
from HABApp.core.internals import EventBusListener, wrap_func
from tests.helpers import TestEventBus


def test_error():
    with pytest.raises(ValueError) as e:
        wrap_func(None)
    assert str(e.value) == 'Callable or coroutine function expected! Got "None" (type NoneType)'

    with pytest.raises(ValueError) as e:
        wrap_func(6)
    assert str(e.value) == 'Callable or coroutine function expected! Got "6" (type int)'

    with pytest.raises(ValueError) as e:
        wrap_func(date(2023, 12, 24))
    assert str(e.value) == 'Callable or coroutine function expected! Got "2023-12-24" (type date)'


def test_sync_run(sync_worker):
    func = Mock()
    f = wrap_func(func, name='mock')
    f.run()
    func.assert_called_once_with()


async def test_async_run():
    coro = AsyncMock()
    f = wrap_func(coro, name='coro_mock')
    f.run()
    await asyncio.sleep(0.05)
    coro.assert_awaited_once()


def test_sync_args(sync_worker):
    func = Mock()
    f = wrap_func(func, name='mock')
    f.run('arg1', 'arg2', kw1='kw1')
    func.assert_called_once_with('arg1', 'arg2', kw1='kw1')


async def test_async_args():
    coro = AsyncMock()
    f = wrap_func(coro, name='coro_mock')
    f.run('arg1', 'arg2', kw1='kw1')

    await asyncio.sleep(0.05)
    coro.assert_awaited_once_with('arg1', 'arg2', kw1='kw1')


def func_div_error():
    1 / 0


async def async_func_div_error():
    1 / 0


@pytest.mark.ignore_log_errors()
@pytest.mark.parametrize(
    'func, name', ((func_div_error, 'func_div_error'), (async_func_div_error, 'async_func_div_error')))
async def test_async_error_wrapper(eb: TestEventBus, name, func, sync_worker):
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
