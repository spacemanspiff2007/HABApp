from dataclasses import dataclass
from time import monotonic
from typing import Final

from .base import BaseRateLimit, BaseRateLimitInfo


@dataclass
class LeakyBucketLimitInfo(BaseRateLimitInfo):
    time_remaining: float  #: Time remaining until the next drop


class LeakyBucketLimit(BaseRateLimit):
    def __init__(self, allowed: int, interval: int, hits: int = 0):
        super().__init__(allowed, interval, hits)

        self.drop_interval: Final = interval / allowed
        self.next_drop: float = -1.0

    def repr_text(self):
        return f'drop_interval={self.drop_interval:.1f}s'

    def do_test_allow(self):

        while self.next_drop <= monotonic():
            self.hits -= 1
            self.next_drop += self.drop_interval

            if self.hits <= 0:
                # out of drop interval -> reset stats
                if self.next_drop <= monotonic():
                    self.next_drop = monotonic() + self.drop_interval
                    self.skips = 0

                self.hits = 0
                break

    do_allow = do_test_allow
    do_deny = None

    def info(self) -> LeakyBucketLimitInfo:
        self.do_test_allow()

        remaining = self.next_drop - monotonic()
        if remaining <= 0:
            remaining = 0

        return LeakyBucketLimitInfo(
            time_remaining=remaining, hits=self.hits, skips=self.skips, limit=self.allowed
        )
