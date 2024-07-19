from typing import Callable

from eascheduler.executors import ExecutorBase

from HABApp.core.internals.wrapped_function import WrappedFunctionBase


class WrappedFunctionExecutor(ExecutorBase):
    def __init__(self, func: Callable, *args, **kwargs):
        assert isinstance(func, WrappedFunctionBase), type(func)
        super().__init__(func, *args, **kwargs)

    def execute(self):
        self._func.run(*self._args, **self._kwargs)
