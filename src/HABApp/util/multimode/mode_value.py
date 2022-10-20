import logging
import typing
from datetime import datetime, timedelta

from .mode_base import BaseMode


class ValueMode(BaseMode):
    """ValueMode

    :ivar datetime.datetime last_update: Timestamp of the last update/enable of this value
    :ivar typing.Optional[datetime.timedelta] auto_disable_after: Automatically disable this mode after
                                                                    a given timedelta on the next recalculation
    :vartype auto_disable_func: typing.Optional[typing.Callable[[typing.Any, typing.Any], bool]]
    :ivar    auto_disable_func: Function which can be used to disable this mode. Any function that accepts two
                                  Arguments can be used. First arg is value with lower priority,
                                  second argument is own value. Return ``True`` to disable this mode.
    :vartype calc_value_func: typing.Optional[typing.Callable[[typing.Any, typing.Any], typing.Any]]
    :ivar    calc_value_func: Function to calculate the new value (e.g. ``min`` or ``max``). Any function that accepts
                                two Arguments can be used. First arg is value with lower priority,
                                second argument is own value.
    """

    def __init__(self, name: str,
                 initial_value=None, enabled: typing.Optional[bool] = None, enable_on_value: bool = True,
                 logger: typing.Optional[logging.Logger] = None,
                 auto_disable_after=None, auto_disable_func=None,
                 calc_value_func=None):
        """

        :param name: Name of the mode
        :param initial_value: initial value of the mode
        :param enabled: initial enabled state of the mode
        :param enable_on_value: If ``True`` (default) setting a value (that is not ``None``) will also enable the mode
        :param logger: logger to log events
        :param auto_disable_after: see variables
        :param auto_disable_func: see variables
        :param calc_value_func: see variables
        """
        assert isinstance(name, str), type(name)
        super().__init__(name)

        self.__value = initial_value
        self.__enabled = False

        self.last_update: datetime = datetime.now()
        self.logger = logger

        # do not call callback for initial value
        if initial_value is not None:
            self.__enabled = True
            self.__value = initial_value
        if enabled is not None:
            assert enabled in (True, False), enabled
            self.__enabled = enabled

        self.__low_prio_value = None

        assert isinstance(enable_on_value, bool), type(enable_on_value)
        self.__enable_on_value: bool = enable_on_value

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
    def set_value(self, value, only_on_change: bool = False):
        """Set new value and recalculate overall value. If ``enable_on_value`` is set, setting a value will also
        enable the mode.

        :param value: new value
        :param only_on_change: will set/enable the mode only if value differs or the mode is disabled
        :returns: False if the value was not set, True otherwise
        """

        # Possibility to set the mode only on change
        if only_on_change:
            change = value != self.__value

            # If we set the same value and the mode is disabled we enable it which counts as a change
            if not change and self.__enable_on_value and not self.__enabled:
                change = True

            if not change:
                return False

        self.__value = value
        self.last_update = datetime.now()

        if self.__enable_on_value and self.__value is not None:
            self.__enabled = True

        if self.logger is not None:
            self.logger.info(f'[{"x" if self.__enabled else " "}] {self.name}: {self.__value}')

        self.parent.calculate_value()
        return True

    def set_enabled(self, value: bool, only_on_change: bool = False) -> bool:
        """Enable or disable this value and recalculate overall value

        :param value: True/False
        :param only_on_change: enable only on change
        :return: True if the value was set else False
        """
        assert isinstance(value, bool), value

        # Possibility to enable/disable only on change
        if only_on_change and (value == self.__value or not self.__enabled):
            return False

        self.__enabled = value
        self.last_update = datetime.now()

        if self.logger is not None:
            self.logger.info(f'[{"x" if self.__enabled else " "}] {self.name}')

        self.parent.calculate_value()
        return True

    def calculate_lower_priority_value(self) -> typing.Any:
        # Trigger recalculation, this way we keep the output of MultiModeValue synchronized
        # in case some mode get enabled/disabled (e.g. by time)
        self.parent.calculate_value()

        return self.__low_prio_value

    def calculate_value(self, value_with_lower_priority: typing.Any) -> typing.Any:

        # helper for self.calculate_lower_priority_value
        self.__low_prio_value = value_with_lower_priority

        # so we don't spam the log if we are already disabled
        if not self.__enabled:
            return value_with_lower_priority

        # Automatically disable after certain time
        if isinstance(self.auto_disable_after, timedelta):
            if datetime.now() > self.last_update + self.auto_disable_after:
                self.__enabled = False
                self.last_update = datetime.now()
                if self.logger is not None:
                    self.logger.info(f'[{"x" if self.__enabled else " "}] {self.name} '
                                     f'(after {self.auto_disable_after})!')

        # provide user function which can disable a mode
        if self.auto_disable_func is not None:
            if self.auto_disable_func(value_with_lower_priority, self.__value) is True:
                self.__enabled = False
                self.last_update = datetime.now()
                if self.logger is not None:
                    self.logger.info(f'[{"x" if self.__enabled else " "}] {self.name} (function)')

        # check if we may have disabled this mode
        if not self.__enabled:
            return value_with_lower_priority

        if self.calc_value_func is None:
            return self.__value
        return self.calc_value_func(value_with_lower_priority, self.__value)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name} enabled: {self.__enabled}, value: {self.__value}>'
