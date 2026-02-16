from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, override

from HABApp.core.asyncio import create_task
from HABApp.core.internals.function_executor._base import FunctionExecutorBase


if TYPE_CHECKING:
    import logging
    from collections.abc import Callable, Coroutine

    from HABApp.core.internals import Context
    from HABApp.core.internals.function_executor.factory import ExecutorFactory


class CoroutineExecutor[**P, R](FunctionExecutorBase[P, R]):
    __slots__ = ('coro', )

    def __init__(self, func: Callable[P, Coroutine[Any, Any, R]], *,
                 name: str | None = None, logger: logging.Logger | None = None,
                 context: Context, factory: ExecutorFactory) -> None:
        super().__init__(func, name=name, logger=logger, context=context, factory=factory)
        self.coro: Final = func

    @override
    async def execute(self, *args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return await self.coro(*args, **kwargs)
        except Exception as e:
            self.process_exception(e, *args, **kwargs)
            return None

    @override
    def execute_background(self, *args: P.args, **kwargs: P.kwargs) -> None:
        create_task(self.execute(*args, **kwargs), name=self.name)
