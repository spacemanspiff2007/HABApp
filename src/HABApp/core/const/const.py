import sys
import time
from enum import Enum
from typing import Final


class _MissingType(Enum):
    MISSING = object()

    def __repr__(self):
        return '<Missing>'


MISSING: Final = _MissingType.MISSING
STARTUP: Final = time.monotonic()

# Python Versions for feature control
PYTHON_38: Final = sys.version_info >= (3, 8)
PYTHON_39: Final = sys.version_info >= (3, 9)
PYTHON_310: Final = sys.version_info >= (3, 10)
PYTHON_311: Final = sys.version_info >= (3, 11)
