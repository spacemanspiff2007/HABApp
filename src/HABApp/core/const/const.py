import sys
from enum import Enum
from typing import Final, Literal

from whenever import Instant


class _MissingType(Enum):
    _MISSING = object()

    def __repr__(self) -> str:
        return '<Missing>'


MISSING: Final = _MissingType._MISSING
type MISSING_TYPE = Literal[_MissingType._MISSING]

STARTUP_INSTANT: Final = Instant.now()

# Python Versions for feature control
PYTHON_313: Final = sys.version_info >= (3, 13)
PYTHON_314: Final = sys.version_info >= (3, 14)
PYTHON_315: Final = sys.version_info >= (3, 15)
