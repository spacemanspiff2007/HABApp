import typing
from threading import Lock


class ValueChanger:
    def __init__(self, parent, value=None):

        self.__parent = parent

        self._value = value
        self._enabled = True if value is not None else False

    def set_value(self, value):
        self._enabled = True if value is not None else False
        self._value = value

        self.__parent._value_changed(self)

    def set_enabled(self, value):
        assert value is True or value is False
        self._enabled = value

        self.__parent._value_changed(self)


class PrioritizedValue:
    def __init__(self, on_change):
        self.on_value_change = on_change

        self.__value = None

        self.__childs: typing.Dict[int, typing.List[ValueChanger]] = {}
        self.__child_list: typing.Dict[ValueChanger, list] = {}
        self.__lock = Lock()

    def add_value(self, priority: int, value=None) -> ValueChanger:

        c = ValueChanger(self, value)

        child_list = self.__childs.setdefault(priority, [])
        child_list.append(c)

        self.__child_list[c] = child_list
        return c

    def _value_changed(self, child):

        # move most recent to the end of the queue if we have multiple entries with the same priority
        with self.__lock:
            child_list = self.__child_list[child]
            if len(child_list) > 1:
                child_list.remove(child)
                child_list.append(child)

        new_value = None
        for prio, child_list in sorted(self.__childs.items()):
            for child in child_list:
                assert isinstance(child, ValueChanger)

                if not child._enabled:
                    continue
                new_value = child._value

        if new_value == self.__value:
            return None

        with self.__lock:
            self.__value = new_value
        self.on_value_change(new_value)
