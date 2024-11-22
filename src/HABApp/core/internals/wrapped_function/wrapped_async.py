import logging
from collections.abc import Callable, Coroutine
from typing import Any, Final

from typing_extensions import override

from HABApp.core.asyncio import async_context, create_task
from HABApp.core.internals import Context
from HABApp.core.internals.wrapped_function.base import P, R, WrappedFunctionBase


class WrappedAsyncFunction(WrappedFunctionBase[P, R]):

    def __init__(self, coro: Callable[P, Coroutine[Any, Any, R]],
                 name: str | None = None,
                 logger: logging.Logger | None = None,
                 context: Context | None = None) -> None:

        super().__init__(name=name, func=coro, logger=logger, context=context)

        self.coro: Final = coro

    @override
    def run(self, *args: P.args, **kwargs: P.kwargs) -> None:
        create_task(self.async_run(*args, **kwargs), name=self.name)

    @override
    async def async_run(self, *args: P.args, **kwargs: P.kwargs) -> R | None:

        token = async_context.set('WrappedAsyncFunction')

        try:
            return await self.coro(*args, **kwargs)
        except Exception as e:
            self.process_exception(e, *args, **kwargs)
            return None
        finally:
            async_context.reset(token)
