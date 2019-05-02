import typing
from threading import Lock


class ValueChanger:
    def __init__(self, parent, initial_value=None):

        self.__parent: PrioritizedValue = parent

        self._value = initial_value
        self._enabled = True if initial_value is not None else False

    def set_value(self, value):
        """Set new value and recalculate overall value

        :param value: new value
        """
        self._enabled = True if value is not None else False
        self._value = value

        self.__parent._value_changed(self)

    def set_enabled(self, value: bool):
        """Enable or disable and recalculate overall value

        :param value: True/False
        """
        assert value is True or value is False
        self._enabled = value

        self.__parent._value_changed(self)

    def __repr__(self):
        return f'<{self.__class__.__name__} enabled: {self._enabled}, value: {self._value}>'


class PrioritizedValue:
    """Thread safe value prioritizer"""
    
    def __init__(self, on_change):
        self.on_value_change = on_change

        self.__value = None

        self.__childs: typing.Dict[int, ValueChanger] = {}
        self.__lock = Lock()

    def get_value_changer(self, priority: int, initial_value=None) -> ValueChanger:
        """ Create a new instance which can be used to set values

        :param priority: priority of the value
        :param initial_value: initial value
        """
        if priority in self.__childs:
            return self.__childs[priority]

        self.__childs[priority] = ret = ValueChanger(self, initial_value)
        return ret

    def _value_changed(self, child):

        # recalculate value
        new_value = None
        with self.__lock:
            for prio, child in sorted(self.__childs.items()):
                assert isinstance(child, ValueChanger)

                if not child._enabled:
                    continue
                new_value = child._value

            value_changed = new_value != self.__value
            self.__value = new_value

        # Notify that the value has changed
        if value_changed:
            self.on_value_change(new_value)
