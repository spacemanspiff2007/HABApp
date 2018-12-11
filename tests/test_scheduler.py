import unittest, typing
from datetime import datetime, timedelta

from .context import HABApp
from HABApp.util import scheduler


class CExecutor:
    def submit(self, callback, *args, **kwargs):
        callback(*args, **kwargs)
executor = CExecutor()

class TestCases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.called = False
        self.last_args : typing.Optional[typing.List] = None
        self.last_kwargs : typing.Optional[typing.Dict] = None


    def setUp(self):
        self.called = False
        self.last_args = None
        self.last_kwargs = None

    def call_func(self, *args, **kwargs):
        self.called = True
        self.last_args = args
        self.last_kwargs = kwargs

    def test_ScheduledCallback(self):
        shed = scheduler.ScheduledCallback(datetime.now() + timedelta(seconds=1), self.call_func, 'T1', F2='F2')
        self.assertIs(shed.check_due(datetime.now()), False)
        self.assertIs(shed.execute(executor), False)
        self.assertIs(self.called, False)
        self.assertEqual(shed.is_finished, False)

        # recheck and run
        self.assertIs(shed.check_due(datetime.now() + timedelta(seconds=1)), True)
        self.assertIs(shed.execute(executor), True)

        # func call
        self.assertIs(self.called, True)
        self.assertEqual( self.last_args, ('T1',))
        self.assertEqual( self.last_kwargs, { 'F2' : 'F2'})

        self.assertEqual(shed.is_finished, True)


if __name__ == '__main__':
    unittest.main()