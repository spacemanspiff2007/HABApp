from threading import Lock

import HABApp


class CounterItem(HABApp.core.items.Item):
    """Implements a simple thread safe counter"""

    # todo: Max Value and events when counter is 0 or has max value

    def __init__(self, name: str, initial_value: int = 0):
        """
        :param initial_value: Initial value of the counter
        """

        self.value: int = initial_value  # this gets overwritten but we provide a type hint anyway

        super().__init__(name=name, initial_value=initial_value)
        assert isinstance(initial_value, int), type(initial_value)

        self.__lock: Lock = Lock()
        self.__initial_value = initial_value

    def set_value(self, new_value) -> bool:
        assert isinstance(new_value, int), type(new_value)
        return super().set_value(new_value)

    def post_value(self, new_value):
        assert isinstance(new_value, int), type(new_value)
        super().post_value(new_value)

    def reset(self):
        """Reset value to initial value"""
        with self.__lock:
            self.post_value(self.__initial_value)
        return self.__initial_value

    def increase(self, step=1) -> int:
        """Increase value

        :param step: increase by this value, default = 1
        :return: value of the counter
        """
        assert isinstance(step, int), type(step)
        with self.__lock:
            self.post_value(self.value + step)
        return self.value

    def decrease(self, step=1) -> int:
        """Decrease value

        :param step: decrease by this value, default = 1
        :return: value of the counter
        """
        assert isinstance(step, int), type(step)
        with self.__lock:
            self.post_value(self.value - step)
        return self.value
