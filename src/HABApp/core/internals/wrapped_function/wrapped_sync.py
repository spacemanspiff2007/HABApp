import logging
from typing import Optional, Callable

from HABApp.core.asyncio import async_context, create_task
from HABApp.core.internals import Context
from .base import WrappedFunctionBase


class WrappedSyncFunction(WrappedFunctionBase):

    def __init__(self, func: Callable,
                 warn_too_long=True,
                 name: Optional[str] = None,
                 logger: Optional[logging.Logger] = None,
                 context: Optional[Context] = None):

        super().__init__(name=name, func=func, logger=logger, context=context)
        assert callable(func)

        self.func = func
        self.warn_too_long: bool = warn_too_long

    def run(self, *args, **kwargs):
        create_task(self.async_run(*args, **kwargs), name=self.name)

    async def async_run(self, *args, **kwargs):

        token = async_context.set('WrappedSyncFunction')

        try:
            self.func(*args, **kwargs)
        except Exception as e:
            self.process_exception(e, *args, **kwargs)
        finally:
            async_context.reset(token)
