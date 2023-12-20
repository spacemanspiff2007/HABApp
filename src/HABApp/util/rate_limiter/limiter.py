from dataclasses import dataclass
from typing import Final, List, Literal, Tuple, TypeAlias, Union

from HABApp.core.const.const import StrEnum

from .limits import (
    BaseRateLimit,
    FixedWindowElasticExpiryLimit,
    FixedWindowElasticExpiryLimitInfo,
    LeakyBucketLimit,
    LeakyBucketLimitInfo,
)
from .parser import parse_limit


class LimitTypeEnum(StrEnum):
    LEAKY_BUCKET = 'leaky_bucket'
    FIXED_WINDOW_ELASTIC_EXPIRY = 'fixed_window_elastic_expiry'


LIMITER_ALGORITHM_HINT: TypeAlias = Literal[LimitTypeEnum.LEAKY_BUCKET, LimitTypeEnum.FIXED_WINDOW_ELASTIC_EXPIRY]


class Limiter:
    def __init__(self, name: str):
        self._name: Final = name
        self._limits: Tuple[BaseRateLimit, ...] = ()
        self._skips = 0

    def __repr__(self):
        return f'<{self.__class__.__name__} {self._name:s}>'

    def add_limit(self, allowed: int, interval: int,
                  algorithm: LIMITER_ALGORITHM_HINT = LimitTypeEnum.FIXED_WINDOW_ELASTIC_EXPIRY) -> 'Limiter':
        """Add a new rate limit

        :param allowed: How many hits are allowed
        :param interval: Interval in seconds
        :param algorithm: Which algorithm should this limit use
        """
        if allowed <= 0 or not isinstance(allowed, int):
            msg = f'Allowed must be an int >= 0, is {allowed} ({type(allowed)})'
            raise ValueError(msg)

        if interval <= 0 or not isinstance(interval, int):
            msg = f'Expire time must be an int >= 0, is {interval} ({type(interval)})'
            raise ValueError(msg)

        algo = LimitTypeEnum(algorithm)
        if algo is LimitTypeEnum.FIXED_WINDOW_ELASTIC_EXPIRY:
            cls = FixedWindowElasticExpiryLimit
        elif algo is LimitTypeEnum.LEAKY_BUCKET:
            cls = LeakyBucketLimit
        else:
            raise ValueError()

        # Check if we have already added an algorithm with these parameters
        for window in self._limits:
            if isinstance(window, cls) and window.allowed == allowed and window.interval == interval:
                return self

        limit = cls(allowed, interval)
        self._limits = tuple(sorted([*self._limits, limit], key=lambda x: x.interval))
        return self

    def parse_limits(self, *text: str,
                     algorithm: LIMITER_ALGORITHM_HINT = LimitTypeEnum.FIXED_WINDOW_ELASTIC_EXPIRY) -> 'Limiter':
        """Add one or more limits in textual form, e.g. ``5 in 60s``, ``10 per hour`` or ``10/15 mins``.
        If the limit does already exist it will not be added again.

        :param text: textual description of limit
        :param algorithm: Which algorithm should these limits use
        """
        for limit in [parse_limit(t) for t in text]:
            self.add_limit(*limit, algorithm=algorithm)
        return self

    def allow(self) -> bool:
        """Test the limit.

        :return: ``True`` if allowed, ``False`` if forbidden
        """
        allow = True
        clear_skipped = True

        if not self._limits:
            msg = 'No limits defined!'
            raise ValueError(msg)

        for limit in self._limits:
            if not limit.allow():
                allow = False
            # allow increments hits, if it's now 1 it was 0 before
            if limit.hits != 1:
                clear_skipped = False

        if clear_skipped:
            self._skips = 0

        if not allow:
            self._skips += 1

        return allow

    def test_allow(self) -> bool:
        """Test the limit without hitting it. Calling this will not increase the hit counter.

        :return: ``True`` if allowed, ``False`` if forbidden
        """
        allow = True
        clear_skipped = True

        if not self._limits:
            msg = 'No limits defined!'
            raise ValueError(msg)

        for limit in self._limits:
            if not limit.test_allow():
                allow = False
            if limit.hits != 0:
                clear_skipped = False

        if clear_skipped:
            self._skips = 0
        return allow

    def info(self) -> 'LimiterInfo':
        """Get some info about the limiter and the defined windows
        """

        return LimiterInfo(
            skips=self._skips,
            limits=[limit.info() for limit in self._limits]
        )


@dataclass
class LimiterInfo:
    skips: int            #: How many entries were skipped
    limits: List[Union[FixedWindowElasticExpiryLimitInfo, LeakyBucketLimitInfo]]    #: Info for every limit
