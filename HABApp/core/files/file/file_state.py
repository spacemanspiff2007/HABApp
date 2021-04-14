from __future__ import annotations

from enum import Enum, auto


class FileState(Enum):
    LOADED = auto()
    FAILED = auto()

    DEPENDENCIES_OK = auto()
    DEPENDENCIES_MISSING = auto()
    PROPERTIES_ERROR = auto()

    PENDING = auto()

    def __str__(self):
        return str(self.name)
