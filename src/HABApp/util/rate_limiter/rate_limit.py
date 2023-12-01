from dataclasses import dataclass
from time import monotonic
from typing import Final


@dataclass
class RateLimitInfo:
    time_remaining: float   #: Time remaining until this window will reset
    hits: int               #: Hits
    skips: int              #: Skips
    limit: int              #: Boundary

    @property
    def hits_remaining(self) -> int:
        return self.limit - self.hits


class RateLimit:
    def __init__(self, allowed: int, expiry: int):
        super().__init__()
        assert allowed > 0, allowed
        assert expiry > 0, expiry

        self.expiry: Final = expiry
        self.allowed: Final = allowed

        self.start: float = -1.0
        self.stop: float = -1.0
        self.hits: int = 0
        self.skips: int = 0

    def __repr__(self):
        return (f'<{self.__class__.__name__} hits={self.hits:d}/{self.allowed:d} '
                f'expiry={self.expiry:d}s window={self.stop - self.start:.0f}s>')

    def allow(self) -> bool:
        now = monotonic()

        if self.stop < now:
            self.hits = 0
            self.skips = 0
            self.start = now
            self.stop = now + self.expiry

        self.hits += 1
        if self.hits <= self.allowed:
            return True

        self.skips += 1
        self.hits = self.allowed
        self.stop = now + self.expiry
        return False

    def test_allow(self) -> bool:
        now = monotonic()

        if self.hits and self.stop < now:
            self.hits = 0
            self.skips = 0

        return self.hits < self.allowed

    def window_info(self) -> RateLimitInfo:
        if self.hits <= 0:
            remaining = self.expiry
        else:
            remaining = self.stop - monotonic()
            if remaining <= 0:
                remaining = 0

        return RateLimitInfo(
            time_remaining=remaining, hits=self.hits, skips=self.skips, limit=self.allowed
        )
