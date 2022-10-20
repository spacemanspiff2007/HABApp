from HABApp.openhab.definitions import OnOffValue
from HABApp.openhab.items.base_item import OpenhabItem
from HABApp.openhab.items.commands import OnOffCommand


class SwitchItem(OpenhabItem, OnOffCommand):
    """SwitchItem which accepts and converts the data types from OpenHAB

    :ivar str name:
    :ivar Tuple[str, ...] value:

    :ivar Optional[str] label:
    :ivar FrozenSet[str] tags:
    :ivar FrozenSet[str] groups:
    :ivar Mapping[str, MetaData] metadata:
    """

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, OnOffValue):
            new_value = new_value.value

        if new_value is not None and new_value != OnOffValue.ON and new_value != OnOffValue.OFF:
            raise ValueError(f'Invalid value for SwitchItem {self.name}: {new_value}')
        return super().set_value(new_value)

    def is_on(self) -> bool:
        """Test value against on-value"""
        return self.value == OnOffValue.ON

    def is_off(self) -> bool:
        """Test value against off-value"""
        return self.value == OnOffValue.OFF

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, SwitchItem):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        elif isinstance(other, int):
            if other and self.is_on():
                return True
            if not other and self.is_off():
                return True
            return False

        return NotImplemented

    def __bool__(self):
        return self.is_on()
