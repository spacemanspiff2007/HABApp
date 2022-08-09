from threading import Lock
from typing import Optional, Dict, Any, Tuple, List

from HABApp.core.const import MISSING
from HABApp.core.items import Item
from .mode_base import HINT_BASE_MODE, BaseMode

LOCK = Lock()


class MultiModeItem(Item):
    """Prioritizer :class:`~HABApp.core.items.Item`
    """

    @classmethod
    def get_create_item(cls, name: str, initial_value=None, default_value=MISSING) -> 'MultiModeItem':
        """Creates a new item in HABApp and returns it or returns the already existing one with the given name

        :param name: item name
        :param initial_value: state the item will have if it gets created
        :param default_value: Default value that will be sent if no mode is active
        :return: The created or existing item
        """
        item = super().get_create_item(name, initial_value)  # type: MultiModeItem
        item._default_value = default_value
        return item

    def __init__(self, name: str, initial_value=None, default_value=MISSING):
        super().__init__(name=name, initial_value=initial_value)

        self.__values_by_prio: Dict[int, HINT_BASE_MODE] = {}
        self.__values_by_name: Dict[str, HINT_BASE_MODE] = {}

        self._default_value = default_value

    def __remove_mode(self, name: str) -> bool:

        # Check if the mode exists
        mode_remove = self.__values_by_name.pop(name, None)
        if mode_remove is None:
            return False

        # Remove parent mapping, so we at least crash if someone attempts to do something with the mode
        mode_remove.parent = None

        # remove priority entry, too
        for prio, mode in self.__values_by_prio.items():
            if mode is mode_remove:
                self.__values_by_prio.pop(prio)
                return True

        raise RuntimeError(f'Mode {name} is missing!')

    def __sort_modes(self):
        # sort by priority and make lower prio known to the mode
        modes = sorted(self.__values_by_prio.items())
        self.__values_by_prio.clear()

        lower_mode: Optional[HINT_BASE_MODE] = None
        for prio, mode in modes:
            self.__values_by_prio[prio] = mode
            mode._set_mode_lower_prio(lower_mode)
            lower_mode = mode

        return None

    def remove_mode(self, name: str) -> bool:
        """Remove mode if it exists

        :param name: name of the mode (case-insensitive)
        :return: True if something was removed, False if nothing was found
        """
        assert isinstance(name, str), type(name)

        with LOCK:
            found = self.__remove_mode(name.lower())
            self.__sort_modes()
            return found

    def add_mode(self, priority: int, mode: HINT_BASE_MODE) -> 'MultiModeItem':
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
            self.__values_by_prio[priority] = mode
            self.__values_by_name[name] = mode
            mode.parent = self

            # resort
            self.__sort_modes()
        return self

    def all_modes(self) -> List[Tuple[int, HINT_BASE_MODE]]:
        """Returns a sorted list containing tuples with the priority and the mode

        :return: List with priorities and modes
        """
        return list(self.__values_by_prio.items())

    def get_mode(self, name: str) -> HINT_BASE_MODE:
        """Returns a created mode

        :param name: name of the mode (case insensitive)
        :return: The requested MultiModeValue
        """
        try:
            return self.__values_by_name[name.lower()]
        except KeyError:
            raise KeyError(f'Unknown mode "{name}"! Available: {", ".join(self.__values_by_name.keys())}') from None

    def calculate_value(self) -> Any:
        """Recalculate the value. If the new value is not ``MISSING`` the calculated value will be set as the item
        state and the corresponding events will be generated.

        :return: new value
        """

        # recalculate value
        new_value = MISSING
        for priority, child in self.__values_by_prio.items():
            new_value = child.calculate_value(new_value)

        # if nothing is set try the default
        if new_value is MISSING:
            new_value = self._default_value

        if new_value is not MISSING:
            self.post_value(new_value)

        return new_value

    def _on_item_removed(self):
        for p, mode in self.all_modes():
            mode.cancel()

        super()._on_item_removed()
