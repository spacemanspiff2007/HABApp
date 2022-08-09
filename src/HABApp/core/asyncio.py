from asyncio import Future as _Future
from asyncio import run_coroutine_threadsafe as _run_coroutine_threadsafe
from contextvars import ContextVar as _ContextVar
from typing import Any as _Any
from typing import Callable as _Callable
from typing import Coroutine as _Coroutine
from typing import Optional as _Optional
from typing import TypeVar as _TypeVar

from HABApp.core.const import loop

async_context = _ContextVar('async_ctx')


class AsyncContextError(Exception):
    def __init__(self, func: _Callable) -> None:
        super().__init__()
        self.func: _Callable = func

    def __str__(self):
        return f'Function "{self.func.__name__}" may not be called from an async context!'


def create_task(coro: _Coroutine, name: _Optional[str] = None) -> _Future:
    if async_context.get(None) is None:
        return _run_coroutine_threadsafe(coro, loop)
    else:
        return loop.create_task(coro, name=name)


_CORO_RET = _TypeVar('_CORO_RET')


def run_coro_from_thread(coro: _Coroutine[_Any, _Any, _CORO_RET], calling: _Callable) -> _CORO_RET:
    # This function call is blocking, so it can't be called in the async context
    if async_context.get(None) is not None:
        raise AsyncContextError(calling)

    fut = _run_coroutine_threadsafe(coro, loop)
    return fut.result()
