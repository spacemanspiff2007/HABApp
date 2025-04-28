from dataclasses import dataclass
from typing import Final


@dataclass
class BaseRateLimitInfo:
    hits: int               #: Hits
    skips: int              #: Skips
    limit: int              #: Boundary

    @property
    def hits_remaining(self) -> int:
        return self.limit - self.hits


class BaseRateLimit:
    def __init__(self, allowed: int, interval: int, hits: int = 0) -> None:
        super().__init__()
        assert allowed > 0, allowed
        assert interval > 0, interval
        assert 0 <= hits <= allowed

        self.interval: Final = interval
        self.allowed: Final = allowed

        self.hits: int = hits
        self.skips: int = 0

    def repr_text(self) -> str:
        return ''

    def __repr__(self) -> str:
        return (
            f'<{self.__class__.__name__} hits={self.hits:d}/{self.allowed:d} interval={self.interval:d}s '
            f'{self.repr_text():s}>'
        )

    def do_test_allow(self) -> None:
        raise NotImplementedError()

    def do_allow(self) -> None:
        raise NotImplementedError()

    def do_deny(self) -> None:
        raise NotImplementedError()

    def info(self) -> BaseRateLimitInfo:
        raise NotImplementedError()

    def allow(self, weight: int = 1) -> bool:
        if not isinstance(weight, int) or weight <= 0:
            msg = f'weight must be an int > 0, is {weight}'
            raise ValueError(msg)

        self.do_allow()

        self.hits += weight
        if self.hits <= self.allowed:
            return True

        self.skips += 1
        self.hits = self.allowed

        if self.do_deny:
            self.do_deny()
        return False

    def test_allow(self, weight: int = 1) -> bool:
        if not isinstance(weight, int) or weight <= 0:
            msg = f'weight must be an int > 0, is {weight}'
            raise ValueError(msg)

        self.do_test_allow()
        return self.hits + weight <= self.allowed
