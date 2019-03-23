import threading
import time


class PeriodCounter:
    def __init__(self, period):
        assert isinstance(period, int)
        self.period = period

        # Thread save
        self.__lock = threading.Lock()
        # funcs which gets called when the counter changes
        self.__on_change = set()

        self.__timestamps = []

    def on_change(self, func, unregister=False):
        assert callable(func)
        if unregister:
            self.__on_change.remove(func)
        else:
            self.__on_change.add(func)

    def __clean_timestamps(self, add=False):
        now = time.time()
        min_ts = now - self.period
        self.__timestamps = [k for k in self.__timestamps if k >= min_ts]
        if add:
            self.__timestamps.append(now)

    def reset(self):
        with self.__lock:
            count_was = len(self.__timestamps)
            self.__timestamps = []
            count_new = len(self.__timestamps)

        if count_was != count_new:
            for func in self.__on_change:
                func()

    def increase(self) -> int:
        with self.__lock:
            count_was = len(self.__timestamps)
            self.__clean_timestamps(add=True)
            count_new = len(self.__timestamps)

        if count_was != count_new:
            for func in self.__on_change:
                func(count_new)

        return count_new

    def get_count(self) -> int:
        with self.__lock:
            count_was = len(self.__timestamps)
            self.__clean_timestamps(add=False)
            count_new = len(self.__timestamps)

        if count_was != count_new:
            for func in self.__on_change:
                func(count_new)

        return count_new
