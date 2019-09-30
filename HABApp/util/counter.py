import threading

from HABApp.core.items import Item


class CounterItem(Item):
    """Implements a thread safe counter"""

    def __init__(self, name: str, initial_value: int = 0):
        """
        :param initial_value: Initial value of the counter
        """
        super().__init__(name=name, initial_value=initial_value)
        assert isinstance(initial_value, (int, float)), type(initial_value)

        self.__lock = threading.Lock()

        self.__initial_value = initial_value
        self.__value = self.__initial_value

        # func which gets called when the counter changes
        self.on_change = None
        if self.on_change:
            self.on_change(self.__value)

    @property
    def value(self) -> int:
        """Current value"""
        return self.__value

    def reset(self):
        """Reset value to initial value"""
        with self.__lock:
            changed = self.__value != self.__initial_value
            self.__value = self.__initial_value
            value = self.__value

        if changed and self.on_change:
            self.on_change(value)

    def increase(self, step=1) -> int:
        """Increase value

        :param step: increase by this value, default = 1
        :return: value of the counter
        """
        with self.__lock:
            self.__value += step
            value = self.__value

        if self.on_change:
            self.on_change(value)
        return value

    def decrease(self, step=1) -> int:
        """Decrease value

        :param step: decrease by this value, default = 1
        :return: value of the counter
        """
        with self.__lock:
            self.__value -= step
            value = self.__value

        if self.on_change:
            self.on_change(value)

        return value
