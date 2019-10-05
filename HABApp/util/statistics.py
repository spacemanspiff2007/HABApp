import collections
import statistics
import time


class Statistics:
    """Calculate mathematical statistics of numerical values.

    :ivar sum: sum of all values
    :ivar min: minimum of all values
    :ivar max: maximum of all values
    :ivar mean: mean of all values
    :ivar median: median of all values
    :ivar last_value: last added value
    :ivar last_change: timestamp the last time a value was added
    """
    def __init__(self, max_age=None, max_samples=None):
        """
        :param max_age:     Maximum age of values in seconds
        :param max_samples: Maximum amount of samples which will be kept
        """

        if max_age is None and max_samples is None:
            raise ValueError('Please specify max age or max samples!')

        self._max_age = max_age

        self.timestamps = collections.deque(maxlen=max_samples)
        self.values = collections.deque(maxlen=max_samples)

        self.sum: float = None
        self.min: float = None
        self.max: float = None

        self.mean: float = None
        self.median: float = None

        self.last_value: float = None
        self.last_change: float = None

    def _remove_old(self):
        if self._max_age is None:
            return None

        # remove too old entries
        now = time.time()
        while self.timestamps and (now - self.timestamps[0]) > self._max_age:
            self.timestamps.popleft()
            self.values.popleft()

    def update(self):
        """update values without adding a new value"""
        self._remove_old()

        __len = len(self.values)

        if not __len:
            self.sum = None
            self.min = None
            self.max = None

            self.mean = None
            self.median = None
        else:
            self.sum = sum(self.values)
            self.min = min(self.values)
            self.max = max(self.values)

            self.mean = statistics.mean(self.values)
            self.median = statistics.median(self.values)

        if __len >= 2:
            self.last_change = self.values[-1] - self.values[-2]
        else:
            self.last_change = None

    def add_value(self, value):
        """Add a new value and recalculate statistical values

        :param value: new value
        """
        assert isinstance(value, (int, float)), type(value)

        self.last_value = value

        self.timestamps.append(time.time())
        self.values.append(value)

        self.update()

    def __repr__(self):
        return f'<Statistics sum: {self.sum:.1f}, min: {self.min:.2f}, max: {self.max:.2f}, ' \
               f'mean: {self.mean:.2f}, median: {self.median:.2f}>'
