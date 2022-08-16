from __future__ import annotations

from enum import Enum, auto


class FileState(Enum):
    LOADED = auto()
    FAILED = auto()

    DEPENDENCIES_OK = auto()
    DEPENDENCIES_MISSING = auto()

    PROPERTIES_INVALID = auto()  # Properties could not be parsed
    PROPERTIES_ERROR = auto()    # Properties specify a file that doesn't exist

    PENDING = auto()
    REMOVED = auto()

    def __str__(self):
        return str(self.name)
