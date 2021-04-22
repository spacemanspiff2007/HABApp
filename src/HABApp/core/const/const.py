import time
from enum import Enum


class _MissingType(Enum):
    MISSING = object()

    def __str__(self):
        return '<Missing>'


# todo: add type final if we go >= python 3.8
MISSING = _MissingType.MISSING
STARTUP = time.time()
