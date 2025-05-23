class CircularReferenceError(Exception):
    def __init__(self, stack: tuple[str, ...]) -> None:
        self.stack = stack

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {" -> ".join(self.stack)}>'


class DependencyDoesNotExistError(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.msg}>'


class AlreadyHandledFileError(Exception):
    pass
