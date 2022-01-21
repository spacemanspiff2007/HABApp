from typing import TypeVar


class WrappedFunctionBase:
    def run(self, *args, **kwargs):
        raise NotImplementedError()


TYPE_WRAPPED_FUNC_OBJ = TypeVar('TYPE_WRAPPED_FUNC_OBJ', bound=WrappedFunctionBase)
