import logging
from typing import Any

from typing_extensions import Self

from HABApp.core.const.topics import TOPIC_ERRORS as _T_ERRORS
from HABApp.core.const.topics import TOPIC_INFOS as _T_INFOS
from HABApp.core.const.topics import TOPIC_WARNINGS as _T_WARNINGS
from HABApp.core.internals import uses_post_event
from HABApp.core.lib import format_exception


post_event = uses_post_event()


def log_error(logger: logging.Logger, text: str) -> None:
    if '\n' in text:
        for line in text.splitlines():
            logger.error(line)
    else:
        logger.error(text)

    post_event(
        _T_ERRORS, text
    )


def log_warning(logger: logging.Logger, text: str) -> None:
    if '\n' in text:
        for line in text.splitlines():
            logger.warning(line)
    else:
        logger.warning(text)

    post_event(
        _T_WARNINGS, text
    )


def log_info(logger: logging.Logger, text: str) -> None:
    if '\n' in text:
        for line in text.splitlines():
            logger.info(line)
    else:
        logger.info(text)

    post_event(
        _T_INFOS, text
    )


class HABAppLogger:
    _LEVEL: int
    _TOPIC: str

    def __init__(self, log: logging.Logger) -> None:
        self.lines: list[str] = []
        self.logger = log

    def add(self, text: str, *args: Any, **kwargs: Any) -> Self:
        self.lines.append(text.format(*args, **kwargs))
        return self

    def add_exception(self, e: Exception, add_traceback: bool = False) -> Self:
        if not add_traceback:
            for line in str(e).splitlines():
                self.lines.append(line)
        else:
            self.lines.extend(format_exception(e))
        return self

    def dump(self) -> bool:
        if not self.lines:
            return False

        if self.logger.isEnabledFor(self._LEVEL):
            for line in self.lines:
                self.logger._log(self._LEVEL, line, [])

        post_event(
            self._TOPIC, '\n'.join(self.lines)
        )
        self.lines.clear()
        return True

    def __bool__(self) -> bool:
        return bool(self.lines)


class HABAppError(HABAppLogger):
    _LEVEL = logging.ERROR
    _TOPIC = _T_ERRORS


class HABAppWarning(HABAppLogger):
    _LEVEL = logging.WARNING
    _TOPIC = _T_WARNINGS


class HABAppInfo(HABAppLogger):
    _LEVEL = logging.INFO
    _TOPIC = _T_INFOS
