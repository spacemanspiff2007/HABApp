from typing import TYPE_CHECKING, Optional, FrozenSet, Mapping

from HABApp.openhab.items.base_item import OpenhabItem, MetaData

if TYPE_CHECKING:
    MetaData = MetaData
    Optional = Optional
    FrozenSet = FrozenSet,
    Mapping = Mapping


class StringItem(OpenhabItem):
    """StringItem which accepts and converts the data types from OpenHAB

    :ivar str name:
    :ivar str value:

    :ivar Optional[str] label:
    :ivar FrozenSet[str] tags:
    :ivar FrozenSet[str] groups:
    :ivar Mapping[str, MetaData] metadata:
    """


class PlayerItem(OpenhabItem):
    """PlayerItem which accepts and converts the data types from OpenHAB

    :ivar str name:
    :ivar str value:

    :ivar Optional[str] label:
    :ivar FrozenSet[str] tags:
    :ivar FrozenSet[str] groups:
    :ivar Mapping[str, MetaData] metadata:
    """
