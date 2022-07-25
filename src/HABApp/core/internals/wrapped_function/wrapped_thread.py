import io
import logging
from cProfile import Profile
from concurrent.futures import ThreadPoolExecutor
from pstats import SortKey
from pstats import Stats
from time import time
from typing import Callable, Any
from typing import Optional

from HABApp.core.internals import HINT_CONTEXT_OBJ
from HABApp.core.const import loop
from .base import WrappedFunctionBase, default_logger

WORKERS: Optional[ThreadPoolExecutor] = None


def create_thread_pool(count: int):
    global WORKERS
    assert isinstance(count, int) and count > 0

    default_logger.debug(f'Starting thread pool with {count:d} threads!')

    stop_thread_pool()
    WORKERS = ThreadPoolExecutor(count, 'HabAppWorker')


def stop_thread_pool():
    global WORKERS
    if WORKERS is not None:
        WORKERS.shutdown()
        WORKERS = None
        default_logger.debug('Thread pool stopped!')


async def run_in_thread_pool(func: Callable):
    return await loop.run_in_executor(
        WORKERS, func
    )


HINT_FUNC_SYNC = Callable[..., Any]


class WrappedThreadFunction(WrappedFunctionBase):

    def __init__(self, func: HINT_FUNC_SYNC,
                 warn_too_long=True,
                 name: Optional[str] = None,
                 logger: Optional[logging.Logger] = None,
                 context: Optional[HINT_CONTEXT_OBJ] = None):

        super(WrappedThreadFunction, self).__init__(name=name, func=func, logger=logger, context=context)
        assert callable(func)

        self.func = func

        self.warn_too_long: bool = warn_too_long
        self.time_submitted: float = 0.0

    def run(self, *args, **kwargs):
        self.time_submitted = time()
        WORKERS.submit(self.run_sync, *args, **kwargs)

    def run_sync(self, *args, **kwargs):
        start = time()

        # notify if we don't process quickly
        if start - self.time_submitted > 0.05:
            self.log.warning(f'Starting of {self.name} took too long: {start - self.time_submitted:.2f}s. '
                             f'Maybe there are not enough threads?')

        # start profiler
        pr = Profile()
        pr.enable()

        # Execute the function
        try:
            self.func(*args, **kwargs)
        except Exception as e:
            self.process_exception(e, *args, **kwargs)
            return None

        # disable profiler
        pr.disable()

        # log warning if execution takes too long
        duration = time() - start
        if self.warn_too_long and duration > 0.8:
            self.log.warning(f'Execution of {self.name} took too long: {duration:.2f}s')

            s = io.StringIO()
            ps = Stats(pr, stream=s).sort_stats(SortKey.CUMULATIVE)
            ps.print_stats(0.1)  # limit to output to 10% of the lines

            for line in s.getvalue().splitlines()[4:]:    # skip the amount of calls and "Ordered by:"
                if line:
                    self.log.warning(line)
