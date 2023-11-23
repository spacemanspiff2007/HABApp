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
PYTHON_312: Final = sys.version_info >= (3, 12)
PYTHON_313: Final = sys.version_info >= (3, 13)


# In python 3.11 there were changes to MyEnum(str, Enum), so we have to use the StrEnum
# https://docs.python.org/3/library/enum.html#enum.StrEnum
if PYTHON_311:
    # noinspection PyUnresolvedReferences
    from enum import StrEnum
else:
    class StrEnum(str, Enum):
        pass
