import logging

import HABApp
from .const import topics


def log_error(logger: logging.Logger, text: str):
    logger.error(text)
    HABApp.core.EventBus.post_event(
        topics.ERRORS, text
    )


def log_warning(logger: logging.Logger, text: str):
    logger.warning(text)
    HABApp.core.EventBus.post_event(
        topics.WARNINGS, text
    )


def log_info(logger: logging.Logger, text: str):
    logger.info(text)
    HABApp.core.EventBus.post_event(
        topics.INFOS, text
    )


class HABAppLogger:
    _LEVEL: int
    _TOPIC: str

    def __init__(self, log: logging.Logger):
        self.lines = []
        self.logger = log

    def add(self, text: str, *args, **kwargs):
        self.lines.append(text.format(*args, **kwargs))
        return self

    def add_exception(self, e: Exception):
        for line in str(e).splitlines():
            self.lines.append(line)
        return self

    def dump(self) -> bool:
        if not self.lines:
            return False

        if self.logger.isEnabledFor(self._LEVEL):
            for line in self.lines:
                self.logger._log(self._LEVEL, line, [])

        HABApp.core.EventBus.post_event(
            self._TOPIC, '\n'.join(self.lines)
        )
        self.lines.clear()
        return True

    def __bool__(self):
        return bool(self.lines)


class HABAppError(HABAppLogger):
    _LEVEL = logging.ERROR
    _TOPIC = topics.ERRORS


class HABAppWarning(HABAppLogger):
    _LEVEL = logging.WARNING
    _TOPIC = topics.WARNINGS


class HABAppInfo(HABAppLogger):
    _LEVEL = logging.INFO
    _TOPIC = topics.INFOS
