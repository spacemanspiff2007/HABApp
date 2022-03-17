import asyncio
import sys
import typing
import unittest
from unittest.mock import MagicMock

import pytest

import HABApp
from HABApp.core.internals import wrap_func
from HABApp.core.events import NoEventFilter
from HABApp.core.const.topics import ERRORS as TOPIC_ERRORS
from HABApp.core.internals.wrapped_function import wrapped_sync
from HABApp.core.internals import EventBusListener

if sys.version_info < (3, 8):
    from mock import AsyncMock
else:
    from unittest.mock import AsyncMock


class TestCases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.func_called = False
        self.last_args: typing.Optional[typing.List] = None
        self.last_kwargs: typing.Optional[typing.Dict] = None

        self.err_func: MagicMock = None

    def setUp(self):
        self.func_called = False
        self.last_args = None
        self.last_kwargs = None

        self.worker = wrapped_sync.WORKERS

        self.err_func: MagicMock = MagicMock()
        self.err_listener = EventBusListener(
            TOPIC_ERRORS, wrap_func(self.err_func, name='ErrMock'), NoEventFilter()
        )
        HABApp.core.EventBus.add_listener(self.err_listener)

        class CExecutor:
            def submit(self, callback, *args, **kwargs):
                callback(*args, **kwargs)
        wrapped_sync.WORKERS = CExecutor()

    def tearDown(self):
        wrapped_sync.WORKERS = self.worker
        HABApp.core.EventBus.remove_listener(self.err_listener)

    def func_call(self, *args, **kwargs):
        self.func_called = True
        self.last_args = args
        self.last_kwargs = kwargs

    async def async_func_call(self, *args, **kwargs):
        self.func_called = True
        self.last_args = args
        self.last_kwargs = kwargs

    def test_sync_run(self):
        f = wrap_func(self.func_call)
        f.run()
        self.assertTrue(self.func_called)

    def test_sync_args(self):
        f = wrap_func(self.func_call)
        f.run('sarg1', 'sarg2', skw1='skw1')
        self.assertTrue(self.func_called)
        self.assertEqual(self.last_args, ('sarg1', 'sarg2'))
        self.assertEqual(self.last_kwargs, {'skw1': 'skw1'})

    def test_exception1(self):
        def tmp():
            1 / 0

        f = wrap_func(tmp)
        self.assertFalse(self.err_func.called)

        f.run()

        self.assertTrue(self.err_func.called)
        err = self.err_func.call_args[0][0]
        assert isinstance(err, HABApp.core.events.habapp_events.HABAppException)
        assert err.func_name == 'tmp'
        assert isinstance(err.exception, ZeroDivisionError)
        assert err.traceback.startswith('File ')


@pytest.mark.asyncio
async def test_async_run():
    coro = AsyncMock()
    f = wrap_func(coro, name='coro_mock')
    f.run()
    await asyncio.sleep(0.05)
    coro.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_args():
    coro = AsyncMock()
    f = wrap_func(coro, name='coro_mock')
    f.run('arg1', 'arg2', kw1='kw1')

    await asyncio.sleep(0.05)
    coro.assert_awaited_once_with('arg1', 'arg2', kw1='kw1')


@pytest.mark.asyncio
async def test_async_error_wrapper():
    async def tmp():
        1 / 0

    f = wrap_func(tmp)
    err_func = AsyncMock()
    err_listener = HABApp.core.impl.EventBusListener(
        TOPIC_ERRORS, wrap_func(err_func, name='ErrMock'), NoEventFilter())
    HABApp.core.EventBus.add_listener(err_listener)

    f.run()
    await asyncio.sleep(0.05)

    assert err_func.called
    err = err_func.call_args[0][0]
    assert isinstance(err, HABApp.core.events.habapp_events.HABAppException)
    assert err.func_name == 'tmp'
    assert isinstance(err.exception, ZeroDivisionError)
    assert err.traceback.startswith('File ')
