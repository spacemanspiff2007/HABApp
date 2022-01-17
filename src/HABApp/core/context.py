from asyncio import Future as _Future
from asyncio import create_task as _create_task
from asyncio import run_coroutine_threadsafe as _run_coroutine_threadsafe
from contextvars import ContextVar as _ContextVar
from typing import Callable as _Callable
from typing import Coroutine as _Coroutine

from HABApp.core.const import loop

async_context = _ContextVar('async_ctx')


class AsyncContextError(Exception):
    def __init__(self, func: _Callable) -> None:
        super().__init__()
        self.func: _Callable = func

    def __str__(self):
        return f'Function "{self.func.__name__}" may not be called from an async context!'


def create_task(coro: _Coroutine) -> _Future:
    if async_context.get(None) is None:
        return _run_coroutine_threadsafe(coro, loop)
    else:
        return _create_task(coro)
