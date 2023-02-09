from typing import TYPE_CHECKING, TypeVar, Optional, Any

import HABApp
from HABApp.core.internals import AutoContextBoundObj


class BaseMode(AutoContextBoundObj):

    def __init__(self, name: str):
        super().__init__()
        self.name: str = name

        self.__mode_lower_prio: Optional[BaseMode] = None

        self.parent: HABApp.util.multimode.MultiModeItem

        # Otherwise the missing assignment shows an error
        if TYPE_CHECKING:
            self.parent = HABApp.util.multimode.MultiModeItem('TYPE_CHECKING')
        return

    def _set_mode_lower_prio(self, mode_lower_prio):
        assert isinstance(mode_lower_prio, BaseMode) or mode_lower_prio is None, type(mode_lower_prio)
        self.__lower_priority_mode = mode_lower_prio

    def calculate_value(self, lower_prio_value: Any) -> Any:
        raise NotImplementedError()

    def cancel(self):
        """Remove the mode from the parent ``MultiModeItem`` and stop processing it
        """
        self._ctx_unlink()
        self.parent.remove_mode(self.name)
        self.parent = None


HINT_BASE_MODE = TypeVar('HINT_BASE_MODE', bound=BaseMode)
