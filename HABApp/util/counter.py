import threading


class Counter:
    def __init__(self, initial_value=0, on_change=None):
        assert isinstance(initial_value, int)

        self.__lock = threading.Lock()

        self.__initial_value = initial_value
        self.__value = self.__initial_value

        # func which gets called when the counter changes
        self.on_change = on_change
        if self.on_change:
            self.on_change(self.__value)

    @property
    def value(self) -> int:
        return self.__value

    def reset(self):
        with self.__lock:
            changed = self.__value != self.__initial_value
            self.__value = self.__initial_value
            value = self.__value

        if changed and self.on_change:
            self.on_change(value)

    def increase(self, step=1):
        with self.__lock:
            self.__value += step
            value = self.__value

        if self.on_change:
            self.on_change(value)

    def decrease(self, step=1):
        with self.__lock:
            self.__value -= step
            value = self.__value

        if self.on_change:
            self.on_change(value)
