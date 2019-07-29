import asyncio
import typing
import unittest
from unittest.mock import MagicMock

from HABApp.core import WrappedFunction


def run_async(coro):
    asyncio.get_event_loop().run_until_complete(coro)


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

    def test_async_run(self):
        async def tmp():
            f = WrappedFunction(self.async_func_call)
            f.run()
        run_async(tmp())
        self.assertTrue(self.func_called)

    def test_async_args(self):
        async def tmp():
            f = WrappedFunction(self.async_func_call)
            f.run('arg1', 'arg2', kw1='kw1')
        run_async(tmp())
        self.assertTrue(self.func_called)
        self.assertEqual(self.last_args, ('arg1', 'arg2'))
        self.assertEqual(self.last_kwargs, {'kw1': 'kw1'})

    def test_exception1(self):
        def tmp():
            1 / 0

        f = WrappedFunction(tmp)
        WrappedFunction.REGISTER_ERROR_CALLBACK( MagicMock())
        self.assertFalse(f._ERROR_CALLBACK._func.called)
        f.run()
        self.assertTrue(f._ERROR_CALLBACK._func.called)

    def test_exception_in_wrapper(self):
        def tmp():
            1 / 0

        def bla(_in):
            raise ValueError('Error in callback!')

        f = WrappedFunction(tmp)
        WrappedFunction.REGISTER_ERROR_CALLBACK( bla)
        f.run()



if __name__ == '__main__':
    import logging
    import sys
    _log = logging.getLogger()
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter("[{asctime:s}] [{name:25s}] {levelname:8s} | {message:s}", style='{'))
    _log.addHandler(ch)
    unittest.main()
