from datetime import timedelta
from time import time
from typing import Union, Optional

from HABApp.core.internals import wrap_func, AutoContextBoundObj


VAL_TYPE = Union[int, float]


class FadeWorker(AutoContextBoundObj):

    def __init__(self, parent: 'Fade', interval: float):
        super().__init__()
        self.parent: 'Fade' = parent
        self.scheduler = self._parent_ctx.rule.run.every(None, interval, self.parent._scheduled_worker)

    def cancel(self):
        self._ctx_unlink()
        self.scheduler.cancel()
        self.scheduler = None

        self.parent._fade_worker = None
        self.parent = None


MIN_STEP_TIME = 0.2


class Fade:
    """Helper to easily fade values up/down

    :ivar min_value: minimum valid value for the fade value
    :ivar max_value: maximum valid value for the fade value
    :ivar callback: Function with one argument that will be automatically called with the new values when the scheduled
                    fade runs
    """
    def __init__(self, callback=None, min_value: VAL_TYPE = 0, max_value: VAL_TYPE = 100):
        self.min_value = min_value
        self.max_value = max_value

        self._fade_start_time = 0
        self._fade_start_value = 0
        self._fade_stop_value = 0
        self._step_duration = 0
        self._fade_factor = 0
        self._fade_finished = True

        self._fade_worker: Optional[FadeWorker] = None
        self.__callback = wrap_func(callback) if callback is not None else None

        self.value = 0

    def setup(self, start_value: VAL_TYPE, stop_value: VAL_TYPE, duration: Union[int, float, timedelta],
              min_step_duration: float = MIN_STEP_TIME, now: Optional[float] = None) -> 'Fade':
        """Calculates everything that is needed to fade a value

        :param start_value: Start value
        :param stop_value:  Stop value
        :param duration: How long shall the fade take
        :param min_step_duration: minimum step duration (min 0.2 secs)
        :param now: time.time() timestamp to sync multiple fades together
        """
        if start_value < self.min_value or start_value > self.max_value:
            raise ValueError('Start value is out of range')
        if stop_value < self.min_value or stop_value > self.max_value:
            raise ValueError('Stop value is out of range')

        if isinstance(duration, timedelta):
            duration = duration.total_seconds()
        assert isinstance(duration, (int, float)) and duration >= 1

        diff = stop_value - start_value
        if not diff:
            raise ValueError('Start value must be different than stop value')

        # If we have a running fade we have to cancel it before changing the used values
        self.stop_fade()

        self._fade_start_value = start_value
        self._fade_stop_value = stop_value

        self._fade_factor = diff / duration
        self._step_duration = max(MIN_STEP_TIME, min_step_duration, 1 / abs(self._fade_factor))

        self._fade_start_time = time() if now is None else now
        self._fade_finished = False
        return self

    def get_value(self, now: Optional[float] = None) -> float:
        """Returns the current value. If the fade is finished it will always return the stop value.

        :param now: time.time() timestamp for which the value shall be returned. Can be used to sync multiple fades
                    together. Not required.
        :return: current value
        """
        if self._fade_finished:
            return self.value

        if now is None:
            now = time()

        assert now > self._fade_start_time
        dur = now - self._fade_start_time
        value = self._fade_start_value + self._fade_factor * dur

        if self._fade_factor < 0:
            if value <= self._fade_stop_value:
                self._fade_finished = True
                value = max(value, self._fade_stop_value)
        else:
            if value >= self._fade_stop_value:
                self._fade_finished = True
                value = min(value, self._fade_stop_value)

        self.value = value = round(value, 2)
        return value

    @property
    def is_finished(self) -> bool:
        """True if the fade is finished"""
        return self._fade_finished

    async def _scheduled_worker(self):
        self.get_value()
        if self._fade_finished:
            self.stop_fade()

        if self.__callback is not None:
            self.__callback.run(self.value)

    def schedule_fade(self) -> 'Fade':
        """Automatically run the fade with the Scheduler. The callback can be used to set the current fade value
        e.g. on an item. Calling this on a running fade will restart the fade
        """
        if self._fade_worker is not None:
            self._fade_worker.cancel()  # This will also set this variable to None, so we don't have to do it

        self._fade_worker = FadeWorker(self, self._step_duration)
        return self

    def stop_fade(self):
        """Stop the scheduled fade. This can be called multiple times without error"""
        if self._fade_worker is None:
            return None
        self._fade_worker.cancel()
