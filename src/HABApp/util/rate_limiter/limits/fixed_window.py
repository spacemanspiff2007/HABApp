from dataclasses import dataclass
from time import monotonic
from typing import override

from .base import BaseRateLimit, BaseRateLimitInfo


@dataclass
class FixedWindowElasticExpiryLimitInfo(BaseRateLimitInfo):
    time_remaining: float   #: Time remaining until this window will reset


class FixedWindowElasticExpiryLimit(BaseRateLimit):
    def __init__(self, allowed: int, interval: int, hits: int = 0) -> None:
        super().__init__(allowed, interval, hits)

        self.start: float = -1.0
        self.stop: float = -1.0

    @override
    def repr_text(self) -> str:
        return f'window={self.stop - self.start:.0f}s'

    @override
    def do_test_allow(self) -> None:
        if self.stop <= monotonic():
            self.hits = 0
            self.skips = 0

    @override
    def do_allow(self) -> None:
        now = monotonic()

        if self.stop <= now:
            self.hits = 0
            self.skips = 0
            self.start = now
            self.stop = now + self.interval

    @override
    def do_deny(self) -> None:
        self.stop = monotonic() + self.interval

    @override
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
