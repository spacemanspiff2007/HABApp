import re
from typing import Tuple


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
