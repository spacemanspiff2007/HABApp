import logging
from typing import List, Tuple


class BufferedLogger:
    def __init__(self):
        self._msgs: List[Tuple[int, str]] = []

    def _log(self, lvl: int, msg: str):
        self._msgs.append((lvl, msg))

    def debug(self, msg: str) -> 'BufferedLogger':
        self._log(logging.DEBUG, msg)
        return self

    def info(self, msg: str) -> 'BufferedLogger':
        self._log(logging.INFO, msg)
        return self

    def warning(self, msg: str) -> 'BufferedLogger':
        self._log(logging.WARNING, msg)
        return self

    def error(self, msg: str) -> 'BufferedLogger':
        self._log(logging.ERROR, msg)
        return self

    def flush(self, logger: logging.Logger):
        for lvl, msg in self._msgs:
            logger.log(lvl, msg)
        self._msgs.clear()
