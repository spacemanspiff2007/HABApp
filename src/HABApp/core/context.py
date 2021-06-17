from contextvars import ContextVar as _ContextVar
from typing import Callable as _Callable

async_context = _ContextVar('async_ctx')


class AsyncContextError(Exception):
    def __init__(self, func: _Callable) -> None:
        super().__init__()
        self.func: _Callable = func

    def __str__(self):
        return f'Function "{self.func.__name__}" may not be called from an async context!'
