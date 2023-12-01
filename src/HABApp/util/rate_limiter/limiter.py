import re
from dataclasses import dataclass
from time import monotonic
from typing import Final, List, Tuple

from .rate_limit import RateLimit, RateLimitInfo


LIMIT_REGEX = re.compile(
    r"""
    \s* ([1-9][0-9]*)
    \s* (/|per|in)
    \s* ([1-9][0-9]*)?
    \s* (s|sec|second|m|min|minute|h|hour|day|month|year)s?
    \s*""",
    re.IGNORECASE | re.VERBOSE,
)


def parse_limit(text: str) -> Tuple[int, int]:
    if not isinstance(text, str) or not (m := LIMIT_REGEX.fullmatch(text)):
        msg = f'Invalid limit string: "{text:s}"'
        raise ValueError(msg)

    count, per, factor, interval = m.groups()

    interval_secs = {
        's': 1, 'sec': 1, 'second': 1, 'm': 60, 'min': 60, 'minute': 60, 'hour': 3600, 'h': 3600,
        'day': 24 * 3600, 'month': 30 * 24 * 3600, 'year': 365 * 24 * 3600
    }[interval]

    return int(count), int(1 if factor is None else factor) * interval_secs


class Limiter:
    def __init__(self, name: str):
        self._name: Final = name
        self._limits: Tuple[RateLimit, ...] = ()
        self._skipped = 0

    def __repr__(self):
        return f'<{self.__class__.__name__} {self._name:s}>'

    def add_limit(self, allowed: int, expiry: int) -> 'Limiter':
        """Add a new rate limit

        :param allowed: How many hits are allowed
        :param expiry: Interval in seconds
        """
        if allowed <= 0 or not isinstance(allowed, int):
            msg = f'Allowed must be an int >= 0, is {allowed} ({type(allowed)})'
            raise ValueError(msg)

        if expiry <= 0 or not isinstance(expiry, int):
            msg = f'Expire time must be an int >= 0, is {expiry} ({type(expiry)})'
            raise ValueError(msg)

        for window in self._limits:
            if window.allowed == allowed and window.expiry == expiry:
                return self

        limit = RateLimit(allowed, expiry)
        self._limits = tuple(sorted([*self._limits, limit], key=lambda x: x.expiry))
        return self

    def parse_limits(self, *text: str) -> 'Limiter':
        """Add one or more limits in textual form, e.g. ``5 in 60s``, ``10 per hour`` or ``10/15 mins``.
        If the limit does already exist it will not be added again.

        :param text: textual description of limit
        """
        for limit in [parse_limit(t) for t in text]:
            self.add_limit(*limit)
        return self

    def allow(self) -> bool:
        """Test the limit.

        :return: True if allowed, False if forbidden
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
            self._skipped = 0

        if not allow:
            self._skipped += 1

        return allow

    def test_allow(self) -> bool:
        """Test the limit without hitting it. Calling this will not increase the hit counter.

        :return: True if allowed, False if forbidden
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
            self._skipped = 0
        return allow

    def info(self) -> 'LimiterInfo':
        """Get some info about the limiter and the defined windows
        """
        now = monotonic()
        remaining = max((w.stop for w in self._limits if w.hits), default=now) - now
        if remaining <= 0:
            remaining = 0

        return LimiterInfo(
            time_remaining=remaining, skipped=self._skipped,
            limits=[limit.window_info() for limit in self._limits]
        )


@dataclass
class LimiterInfo:
    time_remaining: float   #: time remaining until skipped will reset
    skipped: int            #: how many entries were skipped
    limits: List['RateLimitInfo']    # Info for every window
