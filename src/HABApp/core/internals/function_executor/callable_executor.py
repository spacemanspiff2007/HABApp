from __future__ import annotations

from asyncio import get_event_loop
from typing import TYPE_CHECKING, override

from HABApp.core.asyncio import create_task
from HABApp.core.internals.function_executor._base import SyncFunctionExecutorBase
from HABApp.core.internals.function_executor.thread_pool import PoolFunction


if TYPE_CHECKING:

    from HABApp.core.internals.function_executor.factory import PoolExecutorFactory


class CallableExecutor[**P, R](SyncFunctionExecutorBase[P, R]):

    @override
    async def execute(self, *args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return self.func(*args, **kwargs)
        except Exception as e:
            self.process_exception(e, *args, **kwargs)
            return None

    @override
    def execute_background(self, *args: P.args, **kwargs: P.kwargs) -> None:
        create_task(self.execute(*args, **kwargs), name=self.name)


class CallablePoolExecutor[**P, R](SyncFunctionExecutorBase[P, R]):
    _factory: PoolExecutorFactory

    @override
    async def execute(self, *args: P.args, **kwargs: P.kwargs) -> R | None:
        pool = self._factory.pool
        pool_func = PoolFunction(self, pool, self.func, *args, context=self._habapp_ctx, **kwargs)
        return await get_event_loop().run_in_executor(pool, pool_func)

    @override
    def execute_background(self, *args: P.args, **kwargs: P.kwargs) -> None:
        pool = self._factory.pool
        pool_func = PoolFunction(self, pool, self.func, *args, context=self._habapp_ctx, **kwargs)
        pool.submit(pool_func)
        return None
