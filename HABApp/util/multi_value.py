import datetime
import typing
from threading import Lock


class ValueWithPriority:
    def __init__(self, parent, initial_value=None):

        assert isinstance(parent, MultiValue), type(parent)
        self.__parent: MultiValue = parent

        self.__value = None
        self.__enabled = False

        #: Timestamp of the last update/enable of this value
        self.last_update: datetime.datetime = datetime.datetime.now()

        # do not call callback for initial value
        if initial_value is not None:
            self.__enabled = True
            self.__value = initial_value

    @property
    def value(self):
        """Returns the current value"""
        return self.__value

    @property
    def enabled(self) -> bool:
        """Returns if the value is enabled"""
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
        """Enable or disable this value and recalculate overall value

        :param value: True/False
        """
        assert value is True or value is False, value
        self.__enabled = value

        self.last_update = datetime.datetime.now()

        self.__parent.recalculate_value(self)

    def __str__(self):
        return str(self.__value)

    def __repr__(self):
        return f'<{self.__class__.__name__} enabled: {self.__enabled}, value: {self.__value}>'


class MultiValue:
    """Thread safe value prioritizer"""

    def __init__(self, on_value_change=None):
        """

        :param on_value_change: Callback with one arg which will be called on every change
        """
        self.on_value_change = on_value_change

        self.__value = None

        self.__children: typing.Dict[int, ValueWithPriority] = {}
        self.__lock = Lock()

    @property
    def value(self):
        """Returns the current value"""
        return self.__value

    def get_create_value(self, priority: int, initial_value=None) -> ValueWithPriority:
        """ Create a new instance which can be used to set values

        :param priority: priority of the value
        :param initial_value: initial value
        """
        assert isinstance(priority, int), type(priority)

        with self.__lock:
            if priority in self.__children:
                return self.__children[priority]

            self.__children[priority] = ret = ValueWithPriority(self, initial_value)
            return ret

    def recalculate_value(self, child):
        """Recalculate the output value and call the registered callback (if output has changed)

        :param child: child that changed
        :return: output value
        """

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
        if value_changed and self.on_value_change is not None:
            self.on_value_change(new_value)

        return new_value
