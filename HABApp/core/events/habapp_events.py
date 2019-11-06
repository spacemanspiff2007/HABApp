from pathlib import Path


class RequestFileLoadEvent:
    """Request (re-) loading of the specified file

    :ivar str filename: relative filename
    """

    @classmethod
    def from_path(cls, folder: Path, file: Path) -> 'RequestFileLoadEvent':
        return cls(str(file.relative_to(folder)))

    def __init__(self, name: str = None):
        self.filename: str = name

    def get_path(self, parent_folder: Path) -> Path:
        return parent_folder / self.filename

    def __repr__(self):
        return f'<{self.__class__.__name__} filename: {self.filename}>'


class RequestFileUnloadEvent:
    """Request unloading of the specified file

    :ivar str filename: relative filename
    """

    @classmethod
    def from_path(cls, folder: Path, file: Path) -> 'RequestFileUnloadEvent':
        return cls(str(file.relative_to(folder)))

    def __init__(self, name: str = None):
        self.filename: str = name

    def get_path(self, parent_folder: Path) -> Path:
        return parent_folder / self.filename


    def __repr__(self):
        return f'<{self.__class__.__name__} filename: {self.filename}>'


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
