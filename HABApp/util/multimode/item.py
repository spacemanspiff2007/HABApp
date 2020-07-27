import datetime
import logging
import typing
import warnings
from threading import Lock

import HABApp
from HABApp.core.items import Item
from HABApp.rule import get_parent_rule
from .mode_base import BaseMode

LOCK = Lock()


class MultiModeItem(Item):
    """Prioritizer :class:`~HABApp.core.items.Item`

    :ivar logger: Assign a logger to get log messages about the different modes
    """

    @classmethod
    def get_create_item(cls, name: str, logger=None, initial_value=None):
        # added 20.04.2020, van be removed in some time
        if logger is not None:
            warnings.warn("'logger' is deprecated, set logger on the mode instead!", DeprecationWarning, 2)

        return super().get_create_item(name, initial_value)

    def __init__(self, name: str, initial_value=None):
        super().__init__(name=name, initial_value=initial_value)

        self.__values_by_prio: typing.Dict[int, BaseMode] = {}
        self.__values_by_name: typing.Dict[str, BaseMode] = {}

    def __remove_mode(self, name: str) -> bool:

        # Check if the mode exists
        found = self.__values_by_name.pop(name, None)
        if found is None:
            return False

        # Remove parent mapping, so we at least crash if someone attempts to do something with the mode
        found.parent = None

        # remove value entry, too
        for i, f in self.__values_by_prio.items():
            if f is found:
                self.__values_by_prio.pop(i)
                return True
        raise RuntimeError()

    def __sort_modes(self):
        # make the lower priority known to the mode
        low = None
        for _, child in sorted(self.__values_by_prio.items()):  # type: int, BaseMode
            child._set_mode_lower_prio(low)
            low = child
        return None

    def remove_mode(self, name: str) -> bool:
        """Remove mode if it exists

        :param name: name of the mode (case insensitive)
        :return: True if something was removed, False if nothign was found
        """
        assert isinstance(name, str), type(name)

        with LOCK:
            found = self.__remove_mode(name.lower())
            self.__sort_modes()
            return found

    def add_mode(self, priority: int, mode: BaseMode) -> 'MultiModeItem':
        """Add a new mode to the item, if it already exists it will be overwritten

        :param priority: priority of the mode
        :param mode: instance of the MultiMode class
        """
        assert isinstance(priority, int), type(priority)
        assert isinstance(mode, BaseMode), type(mode)

        name = mode.name.lower()

        with LOCK:
            # remove old mode
            self.__remove_mode(name)

            # add new mode
            mode.parent = self
            self.__values_by_prio[priority] = mode
            self.__values_by_name[name] = mode

            # resort
            self.__sort_modes()

        try:
            get_parent_rule().register_cancel_obj(mode)
        except RuntimeError:
            HABApp.core.logger.log_warning(
                logger=logging.getLogger('HABApp'), text='Parent rule not found! '
                f'Automatic unloading of the {self.__class__.__name__} {self.name} will not work!'
            )
        return self

    def all_modes(self) -> typing.List[typing.Tuple[int, BaseMode]]:
        """Returns a sorted list containing tuples with the priority and the mode

        :return: List with priorities and modes
        """
        return sorted(self.__values_by_prio.items())

    def get_mode(self, name: str) -> BaseMode:
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
        with LOCK:
            for priority, child in sorted(self.__values_by_prio.items()):
                new_value = child.calculate_value(new_value)

        if new_value is not None:
            self.post_value(new_value)
        return new_value

    def create_mode(
            self, name: str, priority: int, initial_value: typing.Optional[typing.Any] = None,
            auto_disable_after: typing.Optional[datetime.timedelta] = None,
            auto_disable_func: typing.Optional[typing.Callable[[typing.Any, typing.Any], bool]] = None,
            calc_value_func: typing.Optional[typing.Callable[[typing.Any, typing.Any], typing.Any]] = None
    ):
        warnings.warn("'create_mode' is deprecated, create a mode and pass it to 'add_mode' instead!",
                      DeprecationWarning, 2)

        m = HABApp.util.multimode.ValueMode(name=name, initial_value=initial_value)
        m.auto_disable_after = auto_disable_after
        m.auto_disable_func = auto_disable_func
        m.calc_value_func = calc_value_func

        self.add_mode(priority, m)
        return m
