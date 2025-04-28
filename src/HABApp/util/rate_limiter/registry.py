from __future__ import annotations

from threading import Lock

from .limiter import Limiter


LOCK = Lock()

_LIMITERS: dict[str, Limiter] = {}


def RateLimiter(name: str) -> Limiter:  # noqa: N802
    """Create a new rate limiter or return an already existing one with a given name.

    :param name: case-insensitive name of limiter
    :return: Rate limiter object
    """

    key = name.lower()

    with LOCK:
        if (obj := _LIMITERS.get(key)) is None:
            _LIMITERS[key] = obj = Limiter(name)

    return obj
