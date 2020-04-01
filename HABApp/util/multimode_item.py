import datetime
import logging
import typing
from threading import Lock

from HABApp.core.items import Item


class MultiModeValue:
    """MultiModeValue

    :ivar datetime.datetime last_update: Timestamp of the last update/enable of this value
    :ivar typing.Optional[datetime.timedelta] auto_disable_after: Automatically disable this mode after
                                              a given timedelta on the next recalculation
    :vartype auto_disable_func: typing.Optional[typing.Callable[[typing.Any, typing.Any], bool]]
    :ivar auto_disable_func: Function which can be used to disable this mode. Any function that accepts two
                            Arguments can be used. First arg is value with lower priority, second argument is own value.
                            Return ``True`` to disable this mode.
    :vartype calc_value_func: typing.Optional[typing.Callable[[typing.Any, typing.Any], typing.Any]]
    :ivar calc_value_func: Function to calculate the new value (e.g. ``min`` or ``max``). Any function that accepts two
                           Arguments can be used. First arg is value with lower priority, second argument is own value.
    """

    def __init__(self, parent, name: str, initial_value=None,
                 auto_disable_after=None, auto_disable_func=None,
                 calc_value_func=None):

        assert isinstance(parent, MultiModeItem), type(parent)
        assert isinstance(name, str), type(name)
        self.__lower_priority_mode: typing.Optional[MultiModeValue] = None
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
        self.auto_disable_after: typing.Optional[datetime.timedelta] = auto_disable_after
        self.auto_disable_func: typing.Optional[typing.Callable[[typing.Any, typing.Any], bool]] = auto_disable_func

        self.calc_value_func: typing.Optional[typing.Callable[[typing.Any, typing.Any], typing.Any]] = calc_value_func

    def _set_lower_priority_mode(self, value):
        assert isinstance(value, MultiModeValue) or value is None, type(value)
        self.__lower_priority_mode = value

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

    def calculate_lower_priority_value(self) -> typing.Any:

        # go down to the first item an trigger recalculation, this way we keep the output of MultiModeValue synchronized
        if self.__lower_priority_mode is None:
            self.__parent.calculate_value()
            return None

        lower_mode = self.__lower_priority_mode
        low_prio_value = lower_mode.calculate_lower_priority_value()
        return lower_mode.calculate_value(low_prio_value)

    def calculate_value(self, value_with_lower_priority: typing.Any) -> typing.Any:

        # so we don't spam the log if we are already disabled
        if not self.__enabled:
            return value_with_lower_priority

        # Automatically disable after certain time
        if isinstance(self.auto_disable_after, datetime.timedelta):
            if datetime.datetime.now() > self.last_update + self.auto_disable_after:
                self.__enabled = True
                self.last_update = datetime.datetime.now()
                self.__parent.log(logging.INFO, f'{self.__name} disabled (after {self.auto_disable_after})!')

        # provide user function which can disable a mode
        if self.auto_disable_func is not None:
            if self.auto_disable_func(value_with_lower_priority, self.__value) is True:
                self.__enabled = False
                self.last_update = datetime.datetime.now()
                self.__parent.log(logging.INFO, f'{self.__name} disabled')

        # check if we may have disabled this mode
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
    def get_create_item(cls, name: str, logger: logging.Logger = None):
        item = super().get_create_item(name, None)
        item.logger = logger
        return item

    def __init__(self, name: str, initial_value=None):
        super().__init__(name=name, initial_value=initial_value)

        self.__values_by_prio: typing.Dict[int, MultiModeValue] = {}
        self.__values_by_name: typing.Dict[str, MultiModeValue] = {}

        self.__lock = Lock()

        self.logger: typing.Optional[logging.Logger] = None

    def log(self, level, text, *args, **kwargs):
        if self.logger is not None:
            self.logger.log(level, f'{self.name}: ' + text, *args, **kwargs)

    def create_mode(
            self, name: str, priority: int, initial_value: typing.Optional[typing.Any] = None,
            auto_disable_after: typing.Optional[datetime.timedelta] = None,
            auto_disable_func: typing.Optional[typing.Callable[[typing.Any, typing.Any], bool]] = None,
            calc_value_func: typing.Optional[typing.Callable[[typing.Any, typing.Any], typing.Any]] = None
    ) -> MultiModeValue:
        """Create a new mode with priority

        :param name: Name of the new mode
        :param priority: Priority of the mode
        :param initial_value: Initial value, will also enable the mode
        :param auto_disable_after: Automatically disable the mode after a timedelta if a recalculate is done
                                   See :attr:`~HABApp.util.multimode_item.MultiModeValue`
        :param auto_disable_func: Automatically disable the mode with a custom function
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
                auto_disable_after=auto_disable_after,
                auto_disable_func=auto_disable_func,
                calc_value_func=calc_value_func
            )
            self.__values_by_prio[priority] = ret
            self.__values_by_name[name.lower()] = ret

            # make the lower priority known to the mode
            low = None
            for _, child in sorted(self.__values_by_prio.items()):  # type: int, MultiModeValue
                child._set_lower_priority_mode(low)
                low = child

        return ret

    def get_mode(self, name: str) -> MultiModeValue:
        """Returns a created mode

        :param name: name of the mode (case insensitive)
        :return: The requested MultiModeValue
        """
        try:
            return self.__values_by_name[name.lower()]
        except KeyError:
            raise KeyError(f'Unknown mode "{name}"! Available: {", ".join(self.__values_by_name.keys())}') from None

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

        if new_value is not None:
            self.post_value(new_value)
        return new_value
