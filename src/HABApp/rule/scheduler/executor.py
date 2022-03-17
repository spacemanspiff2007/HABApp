from typing import Callable

from HABApp.core.internals.wrapped_function import WrappedFunctionBase
from eascheduler.executors import ExecutorBase


class WrappedFunctionExecutor(ExecutorBase):
    def __init__(self, func: Callable, *args, **kwargs):
        assert isinstance(func, WrappedFunctionBase), type(func)
        super().__init__(func, *args, **kwargs)

    def execute(self):
        self._func.run(*self._args, **self._kwargs)
