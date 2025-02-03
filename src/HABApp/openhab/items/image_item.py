from collections.abc import Mapping
from typing import TYPE_CHECKING, Final

from HABApp.core.const import MISSING
from HABApp.core.errors import InvalidItemValueError, ItemValueIsNoneError
from HABApp.openhab.definitions import RawType as _RawType
from HABApp.openhab.definitions import RefreshType, UnDefType
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, ValueToOh
from HABApp.openhab.types import RawType


if TYPE_CHECKING:
    Mapping = Mapping       # noqa: PLW0127
    MetaData = MetaData     # noqa: PLW0127


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/items/ImageItem.java
class ImageItem(OpenhabItem):
    """ImageItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar RawType value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    _update_to_oh: Final = ValueToOh('ImageItem', _RawType, UnDefType)
    _command_to_oh: Final = ValueToOh('ImageItem', RefreshType)
    _state_from_oh_str: Final = staticmethod(_RawType.from_oh_str)

    @property
    def image_type(self) -> str:
        """Image type (e.g. jpg or png)"""
        if (v := self.value) is None:
            raise ItemValueIsNoneError.from_item(self)
        return v.type

    @property
    def image_bytes(self) -> bytes:
        """Image bytes"""
        if (v := self.value) is None:
            raise ItemValueIsNoneError.from_item(self)
        return v.data

    def set_value(self, new_value: RawType | tuple[str, bytes] | None) -> bool:

        if isinstance(new_value, RawType):
            return super().set_value(new_value)

        if isinstance(new_value, tuple):
            image_type, image_bytes = new_value
            if not image_type.startswith('image/') or not isinstance(image_bytes, bytes):
                raise InvalidItemValueError.from_item(self, new_value)
            return super().set_value(RawType.create(image_type, image_bytes))

        if new_value is None:
            return super().set_value(new_value)

        raise InvalidItemValueError.from_item(self, new_value)

    def oh_post_update(self, value: bytes = MISSING, image_type: str | None = None) -> None:
        """Post an update to an openHAB image with new image data. Image type is automatically detected,
        in rare cases when this does not work it can be set manually.

        :param value: image data
        :param image_type: (optional) what kind of image, ``jpeg`` or ``png``
        """
        if image_type is not None:
            value = (value, image_type)
        return super().oh_post_update(value)

    def oh_send_command(self, value: bytes = MISSING, image_type: str | None = None) -> None:
        """Send a command to an openHAB image with new image data. Image type is automatically detected,
        in rare cases when this does not work it can be set manually.

        :param value: image data
        :param image_type: (optional) what kind of image, ``jpeg`` or ``png``
        """
        if image_type is not None:
            value = (value, image_type)
        return super().oh_send_command(value)
