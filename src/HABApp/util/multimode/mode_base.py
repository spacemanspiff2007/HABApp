from __future__ import annotations

from typing import TYPE_CHECKING, Any

from HABApp.core.internals import AutoContextBoundObj


if TYPE_CHECKING:
    import HABApp
    from HABApp.util.multimode import MultiModeItem


class BaseMode(AutoContextBoundObj):

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name: str = name

        self._mode_lower_prio: BaseMode | None = None
        self.parent: MultiModeItem | None = None

    def _set_mode_lower_prio(self, mode_lower_prio: BaseMode | None) -> None:
        assert isinstance(mode_lower_prio, BaseMode) or mode_lower_prio is None, type(mode_lower_prio)
        self._lower_priority_mode = mode_lower_prio

    def calculate_value(self, lower_prio_value: Any) -> Any:
        raise NotImplementedError()

    def cancel(self) -> None:
        """Remove the mode from the parent ``MultiModeItem`` and stop processing it
        """
        self._ctx_unlink()

        if (parent := self.parent) is not None:
            self.parent = None
            parent.remove_mode(self.name)

        self._mode_lower_prio = None
