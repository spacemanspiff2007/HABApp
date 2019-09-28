import datetime
import logging
import operator
import typing
from threading import Lock

from HABApp.core.items import Item


class MultiModeValue:
    """MultiModeValue

    :ivar datetime.datetime last_update: Timestamp of the last update/enable of this value
    :ivar typing.Optional[datetime.timedelta] auto_disable_after: Automatically disable this mode after
                                              a given timedelta on the next recalculation
    :ivar typing.Optional[str] auto_disable_on: Automatically disable this mode if the state with lower priority
                               is ``>``, ``>=``, ``<``, ``<=``, ``==`` or ``!=`` than the own value
    :vartype calc_value_func: typing.Optional[typing.Callable[[typing.Any, typing.Any], typing.Any]]
    :ivar calc_value_func: Function to calculate the new value (e.g. ``min`` or ``max``). Any function that accepts two
                           Arguments can be used. First arg is value with lower priority, second argument is own value.
    """
    DISABLE_OPERATORS = {
        '>': operator.gt, '<': operator.lt, '>=': operator.ge, '<=': operator.le,
        '==': operator.eq, '!=': operator.ne, None: None
    }

    def __init__(self, parent, name: str, initial_value=None, auto_disable_on=None, auto_disable_after=None,
                 calc_value_func=None):

        assert isinstance(parent, MultiModeItem), type(parent)
        assert isinstance(name, str), type(name)
        self.__parent: MultiModeItem = parent
        self.__name = name

        self.__value = None
        self.__enabled = False

        self.last_update: datetime.datetime = datetime.datetime.now()

        # do not call callback for initial value
        if initial_value is not None:
            self.__enabled = True
            self.__value = initial_value

        assert isinstance(auto_disable_after, datetime.timedelta) or auto_disable_after is None, \
            type(auto_disable_after)
        assert auto_disable_on in MultiModeValue.DISABLE_OPERATORS, auto_disable_on
        self.auto_disable_after: typing.Optional[datetime.timedelta] = auto_disable_after
        self.auto_disable_on: str = auto_disable_on

        self.calc_value_func: typing.Optional[typing.Callable[[typing.Any, typing.Any], typing.Any]] = calc_value_func

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

        self.__parent.log(logging.INFO, f'{self.__name} set value to {self.__value}')

        self.__parent.calculate_value()

    def set_enabled(self, value: bool):
        """Enable or disable this value and recalculate overall value

        :param value: True/False
        """
        assert value is True or value is False, value
        self.__enabled = value

        self.last_update = datetime.datetime.now()

        self.__parent.log(logging.INFO, f'{self.__name} {"enabled" if self.__enabled else "disabled"}')

        self.__parent.calculate_value()

    def __operator_on_value(self, operator_str: str, low_prio_value):
        try:
            return MultiModeValue.DISABLE_OPERATORS[operator_str](low_prio_value, self.__value)
        except TypeError as e:
            self.__parent.log(logging.WARNING, f'{e}! {low_prio_value}({type(low_prio_value)}) {operator_str:s} '
                              f'{self.__value}({type(self.__value)})')
            return False

    def calculate_value(self, value_with_lower_priority):

        # so we don't spam the log if we are already disabled
        if not self.__enabled:
            return value_with_lower_priority

        # Automatically disable after certain time
        if isinstance(self.auto_disable_after, datetime.timedelta):
            if datetime.datetime.now() > self.last_update + self.auto_disable_after:
                self.__enabled = True
                self.last_update = datetime.datetime.now()
                self.__parent.log(logging.INFO, f'{self.__name} disabled (after {self.auto_disable_after})!')

        # Automatically disable if <> etc.
        if self.auto_disable_on is not None:
            if self.__operator_on_value(self.auto_disable_on, value_with_lower_priority):
                self.__enabled = False
                self.last_update = datetime.datetime.now()
                self.__parent.log(logging.INFO, f'{self.__name} disabled '
                                  f'({value_with_lower_priority}{self.auto_disable_on}{self.__value})!')

        if not self.__enabled:
            return value_with_lower_priority

        if self.calc_value_func is None:
            return self.__value
        return self.calc_value_func(value_with_lower_priority, self.__value)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.__name} enabled: {self.__enabled}, value: {self.__value}>'


class MultiModeItem(Item):
    """Thread safe value prioritizer :class:`~HABApp.core.items.Item`

    :ivar logger: Assign a logger to get log messages about the different modes
    """

    @classmethod
    def get_create_item(cls, name: str, logger: logging.getLoggerClass() = None):
        item = super().get_create_item(name, None)
        item.logger = logger
        return item

    def __init__(self, name: str, state=None):
        super().__init__(name=name, state=state)

        self.__values_by_prio: typing.Dict[int, MultiModeValue] = {}
        self.__values_by_name: typing.Dict[str, MultiModeValue] = {}

        self.__lock = Lock()

        self.logger: typing.Optional[logging._loggerClass] = None

    def log(self, level, text, *args, **kwargs):
        if self.logger is not None:
            self.logger.log(level, f'{self.name}: ' + text, *args, **kwargs)

    def create_mode(
            self, name: str, priority: int, initial_value: typing.Optional[typing.Any] = None,
            auto_disable_on: typing.Optional[str] = None,
            auto_disable_after: typing.Optional[datetime.timedelta] = None,
            calc_value_func: typing.Optional[typing.Callable[[typing.Any, typing.Any], typing.Any]] = None
    ) -> MultiModeValue:
        """Create a new mode with priority

        :param name: Name of the new mode
        :param priority: Priority of the mode
        :param initial_value: Initial value, will also enable the mode
        :param auto_disable_on: Automatically disable the mode if the lower priority state is ``>`` or ``<`` the value.
                                See :attr:`~HABApp.util.multimode_item.MultiModeValue`
        :param auto_disable_after: Automatically disable the mode after a timedelta if a recalculate is done
                                   See :attr:`~HABApp.util.multimode_item.MultiModeValue`
        :param calc_value_func: See :attr:`~HABApp.util.multimode_item.MultiModeValue`
        :return: The newly created MultiModeValue
        """
        # Silently overwrite the values
        # assert not name.lower() in self.__values_by_name, name.lower()
        # assert not priority in self.__values_by_prio, priority

        with self.__lock:
            ret = MultiModeValue(
                self, name,
                initial_value=initial_value,
                auto_disable_on=auto_disable_on, auto_disable_after=auto_disable_after,
                calc_value_func=calc_value_func
            )
            self.__values_by_prio[priority] = ret
            self.__values_by_name[name.lower()] = ret
        return ret

    def get_mode(self, name: str) -> MultiModeValue:
        """Returns a created mode

        :param name: name of the mode (case insensitive)
        :return: The requested MultiModeValue
        """
        return self.__values_by_name[name.lower()]

    def get_value_until(self, mode_to_stop):
        assert isinstance(mode_to_stop, MultiModeValue), type(mode_to_stop)
        new_value = None
        with self.__lock:
            for priority, child in sorted(self.__values_by_prio.items()):
                if child is mode_to_stop:
                    return new_value

                assert isinstance(child, MultiModeValue)
                new_value = child.calculate_value(new_value)
        raise ValueError()

    def calculate_value(self) -> typing.Any:
        """Recalculate the output value and post the state to the event bus (if it is not None)

        :return: new value
        """

        # recalculate value
        new_value = None
        with self.__lock:
            for priority, child in sorted(self.__values_by_prio.items()):
                assert isinstance(child, MultiModeValue)
                new_value = child.calculate_value(new_value)

        # Notify that the value has changed
        if new_value is not None:
            self.post_state(new_value)
        return new_value
