import asyncio
import typing
import unittest
from unittest.mock import MagicMock

import pytest
import re
from asynctest import CoroutineMock

from HABApp.core import WrappedFunction


class FileNameRemover(str):
    REGEX = re.compile(r'^\s+File ".+?$', re.MULTILINE)

    def __eq__(self, other):
        a = FileNameRemover.REGEX.sub('', self)
        b = FileNameRemover.REGEX.sub('', other)
        return a == b


class TestCases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.func_called = False
        self.last_args: typing.Optional[typing.List] = None
        self.last_kwargs: typing.Optional[typing.Dict] = None

    def setUp(self):
        self.func_called = False
        self.last_args = None
        self.last_kwargs = None

        self.worker = WrappedFunction._WORKERS

        class CExecutor:
            def submit(self, callback, *args, **kwargs):
                callback(*args, **kwargs)
        WrappedFunction._WORKERS = CExecutor()

    def tearDown(self):
        WrappedFunction._WORKERS = self.worker

    def func_call(self, *args, **kwargs):
        self.func_called = True
        self.last_args = args
        self.last_kwargs = kwargs

    async def async_func_call(self, *args, **kwargs):
        self.func_called = True
        self.last_args = args
        self.last_kwargs = kwargs

    def test_sync_run(self):
        f = WrappedFunction(self.func_call)
        f.run()
        self.assertTrue(self.func_called)

    def test_sync_args(self):
        f = WrappedFunction(self.func_call)
        f.run('sarg1', 'sarg2', skw1='skw1')
        self.assertTrue(self.func_called)
        self.assertEqual(self.last_args, ('sarg1', 'sarg2'))
        self.assertEqual(self.last_kwargs, {'skw1': 'skw1'})

    def test_exception1(self):
        def tmp():
            1 / 0

        WrappedFunction._EVENT_LOOP = asyncio.get_event_loop()
        f = WrappedFunction(tmp)
        err_func = MagicMock()
        WrappedFunction.REGISTER_ERROR_CALLBACK(err_func)
        self.assertFalse(err_func.called)
        f.run()
        self.assertTrue(err_func.called)
        err_func.assert_called_once_with(FileNameRemover(
            'Error in tmp: division by zero\n'
            'Traceback (most recent call last):\n'
            '\n'
            '    1 / 0\n'
            'ZeroDivisionError: division by zero'
        ))

    def test_exception_in_wrapper(self):
        def tmp():
            1 / 0

        def bla(_in):
            raise ValueError('Error in callback!')

        f = WrappedFunction(tmp)
        WrappedFunction.REGISTER_ERROR_CALLBACK( bla)
        f.run()


@pytest.mark.asyncio
async def test_async_run():
    coro = CoroutineMock()
    WrappedFunction._EVENT_LOOP = asyncio.get_event_loop()
    f = WrappedFunction(coro, name='coro_mock')
    f.run()
    await asyncio.sleep(0.05)
    coro.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_args():
    coro = CoroutineMock()
    WrappedFunction._EVENT_LOOP = asyncio.get_event_loop()
    f = WrappedFunction(coro, name='coro_mock')
    f.run('arg1', 'arg2', kw1='kw1')

    await asyncio.sleep(0.05)
    coro.assert_awaited_once_with('arg1', 'arg2', kw1='kw1')


@pytest.mark.asyncio
async def test_async_error_wrapper():
    async def tmp():
        1 / 0

    f = WrappedFunction(tmp)
    WrappedFunction._EVENT_LOOP = asyncio.get_event_loop()
    err_func = CoroutineMock()
    WrappedFunction.REGISTER_ERROR_CALLBACK(err_func)
    f.run()
    await asyncio.sleep(0.05)
    err_func.assert_awaited_once_with(FileNameRemover(
        'Error in tmp: division by zero\n'
        'Traceback (most recent call last):\n'
        '\n'
        '    1 / 0\n'
        'ZeroDivisionError: division by zero'
    ))

if __name__ == '__main__':
    import logging
    import sys
    _log = logging.getLogger()
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter("[{asctime:s}] [{name:25s}] {levelname:8s} | {message:s}", style='{'))
    _log.addHandler(ch)
    unittest.main()
