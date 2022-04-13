import time
from enum import Enum
from typing import Final


class _MissingType(Enum):
    MISSING = object()

    def __repr__(self):
        return '<Missing>'


MISSING: Final = _MissingType.MISSING
STARTUP = time.time()
