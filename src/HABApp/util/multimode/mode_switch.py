import logging
import typing

import HABApp
from . import ValueMode


class SwitchItemValueMode(ValueMode):
    """SwitchItemMode, same as ValueMode but enabled/disabled of the mode is controlled by a OpenHAB
    :class:`~HABApp.openhab.items.SwitchItem`

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
                 # these are the parameters special to SwitchItemValueMode
                 switch_item: 'HABApp.openhab.items.SwitchItem', invert_switch: bool = False,
                 # default kw-args from the base class
                 initial_value=None,
                 logger: typing.Optional[logging.Logger] = None,
                 auto_disable_after=None, auto_disable_func=None,
                 calc_value_func=None):
        """

        :param name: Name of the mode
        :param switch_item: :class:`~HABApp.openhab.items.SwitchItem` that will enable/disable the mode
        :param invert_switch: invert switch state (e.g. `OFF` -> enabled, default is ``False``)
        :param initial_value: initial value of the mode
        :param logger: logger to log events
        :param auto_disable_after: see variables
        :param auto_disable_func: see variables
        :param calc_value_func: see variables
        """

        assert invert_switch is True or invert_switch is False
        assert isinstance(switch_item, HABApp.openhab.items.SwitchItem), type(switch_item)
        self.__invert_switch: bool = invert_switch

        super().__init__(name=name,
                         initial_value=initial_value,
                         enabled=switch_item.value == ('ON' if not self.__invert_switch else 'OFF'),
                         enable_on_value=False,  # enable_on_value must be pinned False
                         logger=logger,
                         auto_disable_after=auto_disable_after, auto_disable_func=auto_disable_func,
                         calc_value_func=calc_value_func)

        # setup listener as the last thing
        switch_item.listen_event(self.__switch_changed, HABApp.core.events.ValueChangeEventFilter())
        return

    # this is the original enabled method
    __set_enable = ValueMode.set_enabled

    # prevent direct calling
    def set_enabled(self, value: bool, only_on_change: bool = False):
        """"""  # Empty docstring so this function doesn't show up in Sphinx
        raise PermissionError('Enabled is controlled through the switch item!')

    def __switch_changed(self, event):
        self.__set_enable(event.value == ('ON' if not self.__invert_switch else 'OFF'))
