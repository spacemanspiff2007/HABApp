from typing import Final


class __FileEventBase:
    def __init__(self, name: str) -> None:
        self.name: str = name

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} filename: {self.name}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.name == other.name


class RequestFileLoadEvent(__FileEventBase):
    """Request (re-) loading of the specified file

    :ivar str filename: relative filename
    """


class RequestFileUnloadEvent(__FileEventBase):
    """Request unloading of the specified file

    :ivar str filename: relative filename
    """


class HABAppException:
    """Contains information about an Exception that has occurred in HABApp

    :ivar str func_name: name of the function where the error occurred
    :ivar str traceback: traceback
    :ivar Exception exception: Exception
    """
    def __init__(self, func_name: str, exception: Exception, traceback: str) -> None:
        self.func_name: str = func_name
        self.exception: Exception = exception
        self.traceback: str = traceback

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} func_name: {self.func_name}, exception: {self.exception}>'

    def to_str(self) -> str:
        """Create a readable str with all information"""
        return f'Exception in {self.func_name}: {self.exception}\n{self.traceback}'


class HABAppConnectionStateEvent:
    """Contains information about a connection managed by HABApp

    :ivar str connection: name of the connection
    :ivar str state: state of the connection
    """
    def __init__(self, connection: str, state: str) -> None:
        self.connection: Final = connection
        self.state: Final = state

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} connection: {self.connection:s}, state: {self.state:s}>'
