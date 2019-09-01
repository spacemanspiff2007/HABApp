import datetime
import typing
from threading import Lock


class ValueWithPriority:
    def __init__(self, parent, initial_value=None):

        assert isinstance(parent, ValuePrioritizer), type(parent)
        self.__parent: ValuePrioritizer = parent

        self.__value = None
        self.__enabled = False

        self.last_update: datetime.datetime = None

        if initial_value is not None:
            self.set_value(initial_value)

    @property
    def value(self):
        return self.__value

    @property
    def enabled(self):
        return self.__enabled

    def set_value(self, value):
        """Set new value and recalculate overall value

        :param value: new value
        """
        self.__enabled = True if value is not None else False
        self.__value = value

        self.last_update = datetime.datetime.now()

        self.__parent.recalculate_value(self)

    def set_enabled(self, value: bool):
        """Enable or disable and recalculate overall value

        :param value: True/False
        """
        assert value is True or value is False
        self.__enabled = value

        self.last_update = datetime.datetime.now()

        self.__parent.recalculate_value(self)

    def __str__(self):
        return str(self.__value)

    def __repr__(self):
        return f'<{self.__class__.__name__} enabled: {self.__enabled}, value: {self.__value}>'


class ValuePrioritizer:
    """Thread safe value prioritizer"""

    def __init__(self, on_value_change):
        """

        :param on_value_change: Callback with one arg which will be called on every change
        """
        self.on_value_change = on_value_change

        self.__value = None

        self.__children: typing.Dict[int, ValueWithPriority] = {}
        self.__lock = Lock()

    @property
    def value(self):
        return self.__value

    def get_create_value(self, priority: int, initial_value=None) -> ValueWithPriority:
        """ Create a new instance which can be used to set values

        :param priority: priority of the value
        :param initial_value: initial value
        """
        assert isinstance(priority, int), type(priority)

        if priority in self.__children:
            return self.__children[priority]

        self.__children[priority] = ret = ValueWithPriority(self, initial_value)
        return ret

    def recalculate_value(self, child):

        # recalculate value
        new_value = None
        with self.__lock:
            for priority, child in sorted(self.__children.items()):
                assert isinstance(child, ValueWithPriority)

                if not child.enabled:
                    continue
                new_value = child.value

            value_changed = new_value != self.__value
            self.__value = new_value

        # Notify that the value has changed
        if value_changed:
            self.on_value_change(new_value)

        return new_value
