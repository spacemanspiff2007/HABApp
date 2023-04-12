from asyncio import Future as _Future
from asyncio import run_coroutine_threadsafe as _run_coroutine_threadsafe
from contextvars import ContextVar as _ContextVar
from typing import Any as _Any, Callable
from typing import Callable as _Callable
from typing import Coroutine as _Coroutine
from typing import Optional as _Optional
from typing import TypeVar as _TypeVar
from HABApp.core.const import loop
from HABApp.core.const.const import PYTHON_310

if PYTHON_310:
    from typing import ParamSpec as _ParamSpec
else:
    from typing_extensions import ParamSpec as _ParamSpec


async_context = _ContextVar('async_ctx')


class AsyncContextError(Exception):
    def __init__(self, func: _Callable) -> None:
        super().__init__()
        self.func: _Callable = func

    def __str__(self):
        return f'Function "{self.func.__name__}" may not be called from an async context!'


_tasks = set()


def create_task(coro: _Coroutine, name: _Optional[str] = None) -> _Future:
    # https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
    if async_context.get(None) is None:
        f = _run_coroutine_threadsafe(coro, loop)
        f.add_done_callback(_tasks.discard)
        return f
    else:
        t = loop.create_task(coro, name=name)
        t.add_done_callback(_tasks.discard)
        return t


_CORO_RET = _TypeVar('_CORO_RET')


def run_coro_from_thread(coro: _Coroutine[_Any, _Any, _CORO_RET], calling: _Callable) -> _CORO_RET:
    # This function call is blocking, so it can't be called in the async context
    if async_context.get(None) is not None:
        raise AsyncContextError(calling)

    fut = _run_coroutine_threadsafe(coro, loop)
    return fut.result()


P = _ParamSpec('P')
T = _TypeVar('T')


def run_func_from_async(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    # we already have an async context
    if async_context.get(None) is not None:
        return func(*args, **kwargs)

    future = _run_coroutine_threadsafe(_run_func_from_async_helper(func, *args, **kwargs), loop)
    return future.result()


async def _run_func_from_async_helper(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    return func(*args, **kwargs)
