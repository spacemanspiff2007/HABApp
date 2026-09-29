from __future__ import annotations

from threading import Lock
from typing import Final

from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.util.rate_limiter.limiter import Limiter


class RateLimiterRegistry:
    __slots__ = ('_limiters', '_lock')

    def __init__(self) -> None:
        self._lock = Lock()
        self._limiters: Final[dict[str, Limiter]] = {}

    def get_limiter(self, name: str) -> Limiter:
        key = name.lower()
        with self._lock:
            if (obj := self._limiters.get(key)) is None:
                self._limiters[key] = obj = Limiter(name)
        return obj


def RateLimiter(name: str) -> Limiter:  # noqa: N802
    """Create a new rate limiter or return an already existing one with a given name.

    :param name: case-insensitive name of limiter
    :return: Rate limiter object
    """
    return HABAPP_PROVIDER.get_existing(RateLimiterRegistry).get_limiter(name)
