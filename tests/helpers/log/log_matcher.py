import logging
import os
import re
from typing import Final, Iterable, List, Optional, Union

from .log_utils import SimpleLogRecord, get_log_level_name, get_log_level_no


class LogEntryMatcherBase:
    def matches(self, r: SimpleLogRecord):
        raise NotImplementedError()

    def found(self, recs: Iterable[SimpleLogRecord]):
        for r in recs:
            if self.matches(r):
                return True
        return False


class LogLevelMatcher(LogEntryMatcherBase):
    def __init__(self, level: Union[int, str]):
        self.level: Final = get_log_level_no(level)
        self.level_name: Final = get_log_level_name(self.level)

    def matches(self, r: SimpleLogRecord):
        return r.level == self.level

    def __repr__(self):
        return f'<{self.__class__.__name__} level={self.level_name}>'


IS_CI = os.getenv('CI', 'false') == 'true'  # "true" if we run GitHUB actions


class AsyncDebugWarningMatcher(LogEntryMatcherBase):
    def __init__(self):
        self.duration = re.compile(r' took (\d+.\d+) seconds$')
        self.coro = re.compile(r' coro=<(\w+)\(')

    def matches(self, r: SimpleLogRecord):
        if r.name != 'asyncio' or r.level != logging.WARNING or 'Executing <' not in r.msg:
            return False

        if not (m_dur := self.duration.search(r.msg)):
            return False

        # GitHub takes longer, we don't want to fail the tests there
        if IS_CI:
            return True

        # Coro based timeout
        if m_coro := self.coro.search(r.msg):
            coro = m_coro.group(1)
        else:
            coro = 'NO_CORO'

        secs = float(m_dur.group(1))
        if secs < 0.03 or coro == 'async_subprocess_exec' and secs < 0.15:
            return True

        return False

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


class LogEntryMatcher(LogEntryMatcherBase):
    def __init__(self, name: Optional[str], level: Union[int, str], msg: str):
        self.name: Final = name
        self.level: Final = get_log_level_no(level)
        self.level_name: Final = get_log_level_name(self.level)
        self.msg: Final = msg

    def matches(self, r: SimpleLogRecord):
        return (self.name is None or self.name == r.name) and \
            (self.level is None or self.level == r.level) and \
            (self.msg is None or self.msg == r.msg)

    def __repr__(self):
        return f'<{self.__class__.__name__} name={self.name} level={self.level_name} msg={self.msg}>'


class ConsecutiveMatcher(LogEntryMatcherBase):
    def __init__(self, matcher: Iterable[LogEntryMatcherBase]):
        self.matchers: Final = tuple(matcher)
        self.rec_ok: List[SimpleLogRecord] = []

    def matches(self, r: SimpleLogRecord):
        if r in self.rec_ok:
            return True
        self.rec_ok.clear()

        recs = []

        current: Optional[SimpleLogRecord] = None
        for m in self.matchers:
            if current is not None:
                current = current.next
                if current is None:
                    return False
            else:
                current = r

            if not m.matches(current):
                return False

            recs.append(current)

        self.rec_ok = recs
        return True

    def __repr__(self):
        return f'<{self.__class__.__name__} matchers={self.matchers}>'



def create_matcher(name: Union[Iterable[str], Union[str, None]],
                   level: Union[Iterable[Union[str, int]], Union[str, int]],
                   msg: Union[Iterable[str], str]) -> List[LogEntryMatcher]:

    names = [name] if isinstance(name, str) or name is None else name
    levels = [level] if isinstance(level, (str, int)) else level

    ret = []
    for name in names:
        for level in levels:
            if isinstance(msg, str):
                ret.append(LogEntryMatcher(name, level, msg))
            else:
                ret.append(ConsecutiveMatcher(LogEntryMatcher(name, level, msg_part) for msg_part in msg))

    return ret
