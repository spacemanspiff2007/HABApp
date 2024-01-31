from __future__ import annotations

from time import monotonic


class TimeoutNotRunningError(Exception):
    pass


class Timeout:
    __slots__ = ('_timeout', '_started')

    def __init__(self, timeout: float, *, start: bool = True):
        self._timeout: float = timeout
        if self._timeout <= 0:
            raise ValueError()

        self._started: float | None = None if not start else monotonic()

    def __repr__(self):

        decimals = 1 if self._timeout < 10 else 0

        if self._started is None:
            return f'<Timeout {self._timeout:.{decimals:d}f}s>'

        time = monotonic() - self._started
        if time >= self._timeout:
            time = self._timeout
        return f'<Timeout {time:.{decimals:d}f}/{self._timeout:.{decimals:d}f}s>'

    def reset(self):
        """Reset the timeout if it is running"""
        if self._started is not None:
            self._started = monotonic()
        return self

    def start(self):
        """Start the timeout if it is not running"""
        if self._started is None:
            self._started = monotonic()
        return self

    def stop(self):
        """Stop the timeout"""
        self._started = None
        return self

    def set_timeout(self, timeout: float):
        """Set the timeout

        :param timeout: Timeout in seconds
        """
        if self._timeout <= 0:
            raise ValueError()
        self._timeout = timeout
        return self

    def is_running(self) -> bool:
        """ Return whether the timeout is running.

        :return: True if running or False
        """
        return self._started is not None

    def is_expired(self) -> bool:
        """Return whether the timeout is expired, raises an exception if the timeout is not running

        :return: True if expired else False
        """
        if self._started is None:
            raise TimeoutNotRunningError()
        return monotonic() - self._started >= self._timeout

    def is_running_and_expired(self) -> bool:
        """Return whether the timeout is running and expired

        :return: True if expired else False
        """
        return self._started is not None and monotonic() - self._started >= self._timeout

    def remaining(self) -> float:
        """Return the remaining seconds. Raises an exception if the timeout is not running

        :return: Remaining time in seconds or 0 if expired
        """
        if self._started is None:
            raise TimeoutNotRunningError()
        remaining = self._timeout - (monotonic() - self._started)
        return 0 if remaining <= 0 else remaining

    def remaining_or_none(self) -> float | None:
        """Return the remaining seconds. Raises an exception if the timeout is not running

        :return: Remaining time in seconds, 0 if expired or None if not running
        """
        if self._started is None:
            return None
        remaining = self._timeout - (monotonic() - self._started)
        return 0 if remaining <= 0 else remaining
