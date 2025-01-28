from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Final

from immutables import Map

from HABApp.core.const import MISSING
from HABApp.core.errors import InvalidItemValueError
from HABApp.openhab.definitions import RawType, RawValue, RefreshType, UnDefType
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, ValueToOh


if TYPE_CHECKING:
    Mapping = Mapping
    MetaData = MetaData


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/items/ImageItem.java
class ImageItem(OpenhabItem):
    """ImageItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar bytes value: |oh_item_desc_value|
    :ivar str | None image_type: image type (e.g. jpg or png)

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    _update_to_oh: Final = ValueToOh('ImageItem', RawType, UnDefType)
    _command_to_oh: Final = ValueToOh('ImageItem', RefreshType)
    _state_from_oh_str: Final = staticmethod(RawType.from_oh_str)

    def __init__(self, name: str, initial_value: Any = None,
                 label: str | None = None, tags: frozenset[str] = frozenset(), groups: frozenset[str] = frozenset(),
                 metadata: Mapping[str, MetaData] = Map()) -> None:
        super().__init__(name, None, label, tags, groups, metadata)

        # this item is unique because we also save the image type and thus have two states
        self.image_type: str | None = None

        # so we set all fields properly
        if initial_value is not None:
            self.set_value(initial_value)

    def set_value(self, new_value: RawValue | tuple[str, bytes] | None) -> bool:

        if isinstance(new_value, RawValue):
            image_type = new_value.type
            image_bytes = new_value.value
        elif isinstance(new_value, tuple):
            image_type, image_bytes = new_value
        elif new_value is None:
            self.image_type = None
            return super().set_value(new_value)
        else:
            raise InvalidItemValueError.from_item(self, new_value)

        if not image_type.startswith('image/') or not isinstance(image_bytes, bytes):
            raise InvalidItemValueError.from_item(self, new_value)

        # image/png
        self.image_type = image_type = image_type.removeprefix('image/')
        # bytes
        return super().set_value((image_type, image_bytes))

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
