
from HABAppTests import TestBaseRule

from HABApp.core.asyncio import _in_thread


class TestInThread(TestBaseRule):
    """This rule is testing if the file is loaded in a thread"""

    def __init__(self) -> None:
        super().__init__()
        self.add_test('LoadInThread', self.set_result)

        # thread check must happen in __init__ because the test is run with the scheduler
        self.in_thread = _in_thread()

    def set_result(self) -> None:
        if not self.in_thread:
            msg = 'File was not loaded in thread'
            raise RuntimeError(msg)


TestInThread()
