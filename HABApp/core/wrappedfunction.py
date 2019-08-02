import asyncio
import concurrent.futures
import logging
import time
import traceback

default_logger = logging.getLogger('HABApp.Worker')


class WrappedFunction:
    _WORKERS = concurrent.futures.ThreadPoolExecutor(10, 'HabApp_')
    _ERROR_CALLBACK: 'WrappedFunction' = None
    _EVENT_LOOP = None

    @classmethod
    def CLEAR_ERROR_CALLBACK(cls):
        WrappedFunction._ERROR_CALLBACK = None

    @classmethod
    def REGISTER_ERROR_CALLBACK(cls, func):
        assert callable(func)
        WrappedFunction._ERROR_CALLBACK = WrappedFunction(func, name='ERROR_CALLBACK')

    def __init__(self, func, logger=None, warn_too_long=True, name=None):
        assert callable(func)
        self._func = func

        # name of the function
        self.name = self._func.__name__ if not name else name

        self.is_async = asyncio.iscoroutinefunction(self._func)
        if self.is_async:
            if WrappedFunction._EVENT_LOOP is None:
                WrappedFunction._EVENT_LOOP = asyncio.get_event_loop()

        self.__time_submitted = 0.0

        # Allow custom logger
        self.log = default_logger
        if logger:
            assert isinstance(logger, logging.getLoggerClass())
            self.log = logger

        self.__warn_too_long = warn_too_long

    def run(self, *args, **kwargs):
        if self.is_async:
            # schedule run async, we need to pass the event loop because we can create an async-WrappedFunction
            # from a thread!
            asyncio.ensure_future(self.__async_run(*args, **kwargs), loop=WrappedFunction._EVENT_LOOP)
        else:
            self.__time_submitted = time.time()
            WrappedFunction._WORKERS.submit(self.__run, *args, **kwargs)

    def __format_traceback(self, e: Exception):

        # Skip line 1 and 2 since they contain the wrapper:
        # 0:  Traceback (most recent call last):
        # 1:  File "Z:\Python\HABApp\HABApp\core\wrappedfunction.py", line 67, in __run
        # 2:  self._func(*args, **kwargs)
        lines = traceback.format_exc().splitlines()
        del lines[1:3]  # Remove element 1 & 2

        # Add exception
        lines.insert(0, f'Error in {self.name}: {e}')
        for l in lines:
            self.log.error(l)

        # if we have an error callback call it
        if WrappedFunction._ERROR_CALLBACK is not None:
            if self is not WrappedFunction._ERROR_CALLBACK:
                WrappedFunction._ERROR_CALLBACK.run('\n'.join(lines))


    async def __async_run(self, *args, **kwargs):
        try:
            await self._func(*args, **kwargs)
        except Exception as e:
            self.__format_traceback(e)

    def __run(self, *args, **kwargs):

        __start = time.time()

        # notify if we don't process quickly
        if __start - self.__time_submitted > 0.05:
            self.log.warning(f'Starting of {self.name} took too long: {__start - self.__time_submitted:.1f}s. '
                             f'Maybe there are not enough threads?')

        # Execute the function
        try:
            self._func(*args, **kwargs)
        except Exception as e:
            self.__format_traceback(e)

        # log warning if execution takes too long
        __dur = time.time() - __start
        if self.__warn_too_long and __dur > 0.8:
            self.log.warning(f'Execution of {self.name} took too long: {__dur:.1f}s')
