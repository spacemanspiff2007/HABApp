import collections
import statistics
import time


class Statistics:
    def __init__(self, max_age=None, max_samples=None):
        """
        Keep stats
        :param max_age:     Maximum age in seconds
        :param max_samples: Maximum amount of samples
        """

        if max_age is None and max_samples is None:
            raise ValueError('Please specify max age or max samples!')

        self._max_age = max_age

        self.timestamps = collections.deque(maxlen=max_samples)
        self.states = collections.deque(maxlen=max_samples)

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
            self.states.popleft()

    def update(self):
        self._remove_old()

        __len = len(self.states)

        if not __len:
            self.sum = None
            self.min = None
            self.max = None

            self.mean = None
            self.median = None
        else:
            self.sum = sum(self.states)
            self.min = min(self.states)
            self.max = max(self.states)

            self.mean = statistics.mean(self.states)
            self.median = statistics.median(self.states)

        if __len >= 2:
            self.last_change = self.states[-1] - self.states[-2]
        else:
            self.last_change = None

    def add_value(self, value):
        assert isinstance(value, (int, float)), type(value)

        self.last_value = value

        self.timestamps.append(time.time())
        self.states.append(value)

        self.update()

    def __repr__(self):
        return f'<Statistics sum: {self.sum:.1f}, min: {self.min:.2f}, max: {self.max:.2f}, ' \
               f'mean: {self.mean:.2f}, median: {self.median:.2f}>'
