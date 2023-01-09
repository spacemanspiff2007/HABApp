import logging
from dataclasses import dataclass
from logging import LogRecord
from typing import Union, Optional


def get_log_level_no(level: Union[str, int]) -> int:
    if isinstance(level, int):
        return level

    # try getting the level by name
    try:
        return logging._nameToLevel[level]
    except KeyError:
        return logging._nameToLevel[level.upper()]


def get_log_level_name(level: int) -> str:
    try:
        return logging._levelToName[level]
    except KeyError:
        return str(level)


@dataclass
class SimpleLogRecord:
    name: str
    level: int
    msg: str

    rec: LogRecord

    next: Optional['SimpleLogRecord'] = None
    prev: Optional['SimpleLogRecord'] = None

    @classmethod
    def from_rec(cls, r: LogRecord, prev: Optional['SimpleLogRecord'] = None):
        o = cls(name=r.name, level=r.levelno, msg=r.message, rec=r, prev=prev)
        if prev is not None:
            if prev.next is not None:
                raise ValueError()
            prev.next = o
        return o

    def unlink(self):
        if self.prev is None:
            return None
        self.prev.next = None
        self.prev = None
