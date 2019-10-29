from pathlib import Path


class RequestFileLoadEvent:

    @classmethod
    def from_path(cls, folder: Path, file: Path) -> 'RequestFileLoadEvent':
        return cls(str(file.relative_to(folder)))

    def __init__(self, name: str = None):
        self.filename: str = name

    def __repr__(self):
        return f'<{self.__class__.__name__} filename: {self.filename}>'


class RequestFileUnloadEvent:

    @classmethod
    def from_path(cls, folder: Path, file: Path) -> 'RequestFileUnloadEvent':
        return cls(str(file.relative_to(folder)))

    def __init__(self, name: str = None):
        self.filename: str = name

    def __repr__(self):
        return f'<{self.__class__.__name__} filename: {self.filename}>'
