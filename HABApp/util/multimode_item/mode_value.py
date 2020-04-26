import logging
import typing
from datetime import datetime, timedelta

from .mode_base import BaseMode


# initial_value: typing.Optional[typing.Any] = None,
# auto_disable_after: typing.Optional[datetime.timedelta] = None,
# auto_disable_func: typing.Optional[typing.Callable[[typing.Any, typing.Any], bool]] = None,
# calc_value_func: typing.Optional[typing.Callable[[typing.Any, typing.Any], typing.Any]] = None
# ) -> MultiModeValue: \
#     """Create a new mode with priority
#
# :param name: Name of the new mode
# :param priority: Priority of the mode
# :param initial_value: Initial value, will also enable the mode
# :param auto_disable_after: Automatically disable the mode after a timedelta if a recalculate is done
#                            See :attr:`~HABApp.util.multimode_item.MultiModeValue`
# :param auto_disable_func: Automatically disable the mode with a custom function
#                            See :attr:`~HABApp.util.multimode_item.MultiModeValue`
# :param calc_value_func: See :attr:`~HABApp.util.multimode_item.MultiModeValue`
# :return: The newly created MultiModeValue
# """
#


class ValueModeMode(BaseMode):
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

    def __init__(self, name: str, initial_value=None, logger: typing.Optional[logging.Logger] = None,
                 auto_disable_after=None, auto_disable_func=None,
                 calc_value_func=None):
        assert isinstance(name, str), type(name)
        super().__init__(name)

        self.__name = name
        self.__value = initial_value
        self.__enabled = False

        self.__low_prio_value = None

        self.last_update: datetime = datetime.now()
        self.logger = logger

        # do not call callback for initial value
        if initial_value is not None:
            self.__enabled = True
            self.__value = initial_value

        assert isinstance(auto_disable_after, timedelta) or auto_disable_after is None, type(auto_disable_after)
        self.auto_disable_after: typing.Optional[timedelta] = auto_disable_after
        self.auto_disable_func: typing.Optional[typing.Callable[[typing.Any, typing.Any], bool]] = auto_disable_func

        self.calc_value_func: typing.Optional[typing.Callable[[typing.Any, typing.Any], typing.Any]] = calc_value_func

    @property
    def value(self):
        """Returns the current value"""
        return self.__value

    @property
    def enabled(self) -> bool:
        """Returns if the value is enabled"""
        return self.__enabled

    # we don't use the setter here because of stupid inheritance
    # https://gist.github.com/Susensio/979259559e2bebcd0273f1a95d7c1e79
    def set_value(self, value):
        """Set new value and recalculate overall value

        :param value: new value
        """
        self.__enabled = True if value is not None else False
        self.__value = value

        self.last_update = datetime.now()

        if self.logger is not None:
            self.logger.info(f'{self.__name} set value to {self.__value}')

        self.parent.calculate_value()
        return

    def set_enabled(self, value: bool):
        """Enable or disable this value and recalculate overall value

        :param value: True/False
        """
        assert value is True or value is False, value
        self.__enabled = value

        self.last_update = datetime.now()

        if self.logger is not None:
            self.logger.info(f'{self.__name} {"enabled" if self.__enabled else "disabled"}')

        self.parent.calculate_value()

    def calculate_lower_priority_value(self) -> typing.Any:

        self.__low_prio_value = True

        # Trigger recalculation, this way we keep the output of MultiModeValue synchronized
        # in case some mode gets enabled/disabled/etc
        self.parent.calculate_value()

        val = self.__low_prio_value
        self.__low_prio_value = None
        return val

    def calculate_value(self, value_with_lower_priority: typing.Any) -> typing.Any:
        # helper for self.calculate_lower_priority_value
        if self.__low_prio_value is not None:
            self.__low_prio_value = value_with_lower_priority

        # so we don't spam the log if we are already disabled
        if not self.__enabled:
            return value_with_lower_priority

        # Automatically disable after certain time
        if isinstance(self.auto_disable_after, timedelta):
            if datetime.now() > self.last_update + self.auto_disable_after:
                self.__enabled = True
                self.last_update = datetime.now()
                if self.logger is not None:
                    self.logger.info(f'{self.__name} disabled (after {self.auto_disable_after})!')

        # provide user function which can disable a mode
        if self.auto_disable_func is not None:
            if self.auto_disable_func(value_with_lower_priority, self.__value) is True:
                self.__enabled = False
                self.last_update = datetime.now()
                if self.logger is not None:
                    self.logger.info(f'{self.__name} disabled')

        # check if we may have disabled this mode
        if not self.__enabled:
            return value_with_lower_priority

        if self.calc_value_func is None:
            return self.__value
        return self.calc_value_func(value_with_lower_priority, self.__value)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.__name} enabled: {self.__enabled}, value: {self.__value}>'
