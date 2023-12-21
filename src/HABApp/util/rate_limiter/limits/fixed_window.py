from dataclasses import dataclass
from time import monotonic

from .base import BaseRateLimit, BaseRateLimitInfo


@dataclass
class FixedWindowElasticExpiryLimitInfo(BaseRateLimitInfo):
    time_remaining: float   #: Time remaining until this window will reset


class FixedWindowElasticExpiryLimit(BaseRateLimit):
    def __init__(self, allowed: int, interval: int, hits: int = 0):
        super().__init__(allowed, interval, hits)

        self.start: float = -1.0
        self.stop: float = -1.0

    def repr_text(self):
        return f'window={self.stop - self.start:.0f}s'

    def do_test_allow(self):
        if self.stop <= monotonic():
            self.hits = 0
            self.skips = 0

    def do_allow(self):
        now = monotonic()

        if self.stop <= now:
            self.hits = 0
            self.skips = 0
            self.start = now
            self.stop = now + self.interval

    def do_deny(self):
        self.stop = monotonic() + self.interval

    def info(self) -> FixedWindowElasticExpiryLimitInfo:
        self.do_test_allow()

        remaining = self.stop - monotonic()
        if remaining <= 0:
            remaining = 0

        if not remaining and not self.hits:
            remaining = self.interval

        return FixedWindowElasticExpiryLimitInfo(
            time_remaining=remaining, hits=self.hits, skips=self.skips, limit=self.allowed
        )
