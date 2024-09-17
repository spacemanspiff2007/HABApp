import logging

from typing_extensions import override

from HABApp.core.asyncio import async_context, create_task
from HABApp.core.const.hints import TYPE_FUNC_ASYNC
from HABApp.core.internals import Context

from .base import WrappedFunctionBase


class WrappedAsyncFunction(WrappedFunctionBase):

    def __init__(self, func: TYPE_FUNC_ASYNC,
                 name: str | None = None,
                 logger: logging.Logger | None = None,
                 context: Context | None = None):

        super().__init__(name=name, func=func, logger=logger, context=context)
        assert callable(func)

        self.func = func

    @override
    def run(self, *args, **kwargs):
        create_task(self.async_run(*args, **kwargs), name=self.name)

    @override
    async def async_run(self, *args, **kwargs):

        token = async_context.set('WrappedAsyncFunction')

        try:
            await self.func(*args, **kwargs)
        except Exception as e:
            self.process_exception(e, *args, **kwargs)
        finally:
            async_context.reset(token)
