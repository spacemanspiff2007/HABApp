from typing import Iterable as _Iterable


class CircularReferenceError(Exception):
    def __init__(self, stack: _Iterable[str]):
        self.stack = stack

    def __repr__(self):
        return f'<{self.__class__.__name__} {" -> ".join(self.stack)}>'


class DependencyDoesNotExistError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.msg}>'


class AlreadyHandledFileError(Exception):
    pass
