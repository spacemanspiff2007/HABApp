import HABApp
from pathlib import Path


class __FileEventBase:

    @classmethod
    def from_path(cls, path: Path) -> '__FileEventBase':
        return cls(HABApp.core.files.name_from_path(path))

    def __init__(self, name: str):
        self.name: str = name

    def get_path(self) -> Path:
        return HABApp.core.files.path_from_name(self.name)

    def __repr__(self):
        return f'<{self.__class__.__name__} filename: {self.name}>'


class RequestFileLoadEvent(__FileEventBase):
    """Request (re-) loading of the specified file

    :ivar str filename: relative filename
    """


class RequestFileUnloadEvent(__FileEventBase):
    """Request unloading of the specified file

    :ivar str filename: relative filename
    """


class HABAppError:
    """Contains information about an error in a function

    :ivar str func_name: name of the function where the error occurred
    :ivar str traceback: traceback
    :ivar Exception exception: Exception
    """
    def __init__(self, func_name: str, exception: Exception, traceback: str):
        self.func_name: str = func_name
        self.exception: Exception = exception
        self.traceback: str = traceback

    def __repr__(self):
        return f'<{self.__class__.__name__} func_name: {self.func_name}, exception: {self.exception}>'

    def to_str(self) -> str:
        """Create a readable str with all information"""
        return f'Error in {self.func_name}: {self.exception}\n{self.traceback}'
