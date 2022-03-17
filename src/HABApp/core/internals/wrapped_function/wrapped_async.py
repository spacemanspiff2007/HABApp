import logging
from typing import Optional, Callable, Awaitable, Any, TYPE_CHECKING

from HABApp.core.asyncio import async_context, create_task
from .base import WrappedFunctionBase
from HABApp.core.internals import TYPE_CONTEXT_OBJ

if TYPE_CHECKING:
    import HABApp


TYPE_HINT_FUNC_ASYNC = Callable[..., Awaitable[Any]]


class WrappedAsyncFunction(WrappedFunctionBase):

    def __init__(self, func: TYPE_HINT_FUNC_ASYNC,
                 name: Optional[str] = None,
                 logger: Optional[logging.Logger] = None,
                 context: Optional[TYPE_CONTEXT_OBJ] = None):

        super(WrappedAsyncFunction, self).__init__(name=name, func=func, logger=logger, context=context)
        assert callable(func)

        self.func = func

    def run(self, *args, **kwargs):
        create_task(self.async_run(*args, **kwargs), name=self.name)

    async def async_run(self, *args, **kwargs):

        token = async_context.set('WrappedAsyncFunction')

        try:
            await self.func(*args, **kwargs)
        except Exception as e:
            self.process_exception(e, *args, **kwargs)

        async_context.reset(token)
        return None
