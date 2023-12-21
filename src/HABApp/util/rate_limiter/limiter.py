from dataclasses import dataclass
from typing import Final, List, Literal, Tuple, Union, get_args

from HABApp.core.const.const import PYTHON_310
from HABApp.util.rate_limiter.limits import BaseRateLimit, FixedWindowElasticExpiryLimit, \
    FixedWindowElasticExpiryLimitInfo, LeakyBucketLimit, LeakyBucketLimitInfo
from HABApp.util.rate_limiter.parser import parse_limit

if PYTHON_310:
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias


_LITERAL_LEAKY_BUCKET = Literal['leaky_bucket']
_LITERAL_FIXED_WINDOW_ELASTIC_EXPIRY = Literal['fixed_window_elastic_expiry']

LIMITER_ALGORITHM_HINT: TypeAlias = Literal[_LITERAL_LEAKY_BUCKET, _LITERAL_FIXED_WINDOW_ELASTIC_EXPIRY]


def _check_arg(name: str, value, allow_0=False):
    if not isinstance(value, int) or ((value <= 0) if not allow_0 else (value < 0)):
        msg = f'Parameter {name:s} must be an int >{"=" if allow_0 else ""} 0, is {value} ({type(value)})'
        raise ValueError(msg)


class Limiter:
    def __init__(self, name: str):
        self._name: Final = name
        self._limits: Tuple[BaseRateLimit, ...] = ()
        self._skips = 0

    def __repr__(self):
        return f'<{self.__class__.__name__} {self._name:s}>'

    def add_limit(self, allowed: int, interval: int, *,
                  hits: int = 0,
                  algorithm: LIMITER_ALGORITHM_HINT = 'leaky_bucket') -> 'Limiter':
        """Add a new rate limit

        :param allowed: How many hits are allowed
        :param interval: Interval in seconds
        :param hits: How many hits the limit already has when it gets initially created
        :param algorithm: Which algorithm should this limit use
        """
        _check_arg('allowed', allowed)
        _check_arg('interval', interval)
        _check_arg('hits', hits, allow_0=True)
        if not hits <= allowed:
            msg = f'Parameter hits must be <= parameter allowed! {hits:d} <= {allowed:d}!'
            raise ValueError(msg)

        if algorithm == get_args(_LITERAL_LEAKY_BUCKET)[0]:
            cls = LeakyBucketLimit
        elif algorithm == get_args(_LITERAL_FIXED_WINDOW_ELASTIC_EXPIRY)[0]:
            cls = FixedWindowElasticExpiryLimit
        else:
            msg = f'Unknown algorithm "{algorithm}"'
            raise ValueError(msg)

        # Check if we have already added an algorithm with these parameters
        for window in self._limits:
            if isinstance(window, cls) and window.allowed == allowed and window.interval == interval:
                return self

        limit = cls(allowed, interval, hits=hits)
        self._limits = tuple(sorted([*self._limits, limit], key=lambda x: x.interval))
        return self

    def parse_limits(self, *text: str,
                     hits: int = 0,
                     algorithm: LIMITER_ALGORITHM_HINT = 'leaky_bucket') -> 'Limiter':
        """Add one or more limits in textual form, e.g. ``5 in 60s``, ``10 per hour`` or ``10/15 mins``.
        If the limit does already exist it will not be added again.

        :param text: textual description of limit
        :param hits: How many hits the limit already has when it gets initially created
        :param algorithm: Which algorithm should these limits use
        """
        for limit in [parse_limit(t) for t in text]:
            self.add_limit(*limit, hits=hits, algorithm=algorithm)
        return self

    def allow(self) -> bool:
        """Test the limit(s).

        :return: ``True`` if allowed, ``False`` if forbidden
        """
        if not self._limits:
            msg = 'No limits defined!'
            raise ValueError(msg)

        clear_skipped = True

        for limit in self._limits:
            if not limit.allow():
                self._skips += 1
                return False

            # allow increments hits, if it's now 1 it was 0 before
            if limit.hits != 1:
                clear_skipped = False

        if clear_skipped:
            self._skips = 0

        return True

    def test_allow(self) -> bool:
        """Test the limit(s) without hitting it. Calling this will not increase the hit counter.

        :return: ``True`` if allowed, ``False`` if forbidden
        """

        if not self._limits:
            msg = 'No limits defined!'
            raise ValueError(msg)

        clear_skipped = True

        for limit in self._limits:
            if not limit.test_allow():
                return False

            if limit.hits != 0:
                clear_skipped = False

        if clear_skipped:
            self._skips = 0
        return True

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
