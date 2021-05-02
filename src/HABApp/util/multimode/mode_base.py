import typing


class BaseMode:

    def __init__(self, name: str):
        self.name: str = name

        self.__mode_lower_prio: typing.Optional[BaseMode] = None

        self.parent: MultiModeItem

        # Otherwise the missing assignment shows an error
        if typing.TYPE_CHECKING:
            self.parent = MultiModeItem('TYPE_CHECKING')
        return

    def _set_mode_lower_prio(self, mode_lower_prio):
        assert isinstance(mode_lower_prio, BaseMode) or mode_lower_prio is None, type(mode_lower_prio)
        self.__lower_priority_mode = mode_lower_prio

    def calculate_value(self, lower_prio_value: typing.Any) -> typing.Any:
        raise NotImplementedError()

    def cancel(self):
        """Remove the mode from the parent ``MultiModeItem`` and stop processing it
        """
        self.parent.remove_mode(self.name)
        self.parent = None


from .item import MultiModeItem  # noqa: E402
