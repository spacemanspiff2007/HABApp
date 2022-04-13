from base64 import b64encode
from typing import FrozenSet, Mapping, Optional

from immutables import Map

from HABApp.openhab.items.base_item import OpenhabItem, MetaData
from ..definitions import RawValue


def _convert_bytes(data: bytes, img_type: Optional[str]) -> str:
    assert isinstance(data, bytes), type(data)

    # try to automatically found out what kind of file we have
    if img_type is None:
        if data.startswith(b'\xFF\xD8\xFF'):
            img_type = 'jpeg'
        elif data.startswith(b'\x89\x50\x4E\x47'):
            img_type = 'png'
    assert img_type in ('jpeg', 'png'), f'Image type: "{img_type}", File Signature: {data[:10].hex()}'

    return f'data:image/{img_type:s};base64,{b64encode(data).decode("ascii")}'


class ImageItem(OpenhabItem):
    """ImageItem which accepts and converts the data types from OpenHAB

    :ivar str name:
    :ivar bytes value:
    :ivar Optional[str] image_type:

    :ivar Optional[str] label:
    :ivar FrozenSet[str] tags:
    :ivar FrozenSet[str] groups:
    :ivar Mapping[str, MetaData] metadata:
    """

    def __init__(self, name: str, initial_value=None,
                 label: Optional[str] = None, tags: FrozenSet[str] = frozenset(), groups: FrozenSet[str] = frozenset(),
                 metadata: Mapping[str, MetaData] = Map()):
        super().__init__(name, initial_value, label, tags, groups, metadata)

        # this item is unique because we also save the image type and thus have two states
        self.image_type: Optional[str] = None

    @classmethod
    def from_oh(cls, name: str, value=None, label: Optional[str] = None, tags: FrozenSet[str] = frozenset(),
                groups: FrozenSet[str] = frozenset(), metadata: Mapping[str, MetaData] = Map()):

        c = cls(name, value, label=label, tags=tags, groups=groups, metadata=metadata)
        if value is not None:
            c.set_value(RawValue(value))
        return c

    def set_value(self, new_value) -> bool:
        assert isinstance(new_value, RawValue) or new_value is None, type(new_value)

        if new_value is None:
            self.image_type = None
            return super().set_value(new_value)

        # image/png
        self.image_type = new_value.type
        if self.image_type.startswith('image/'):
            self.image_type = self.image_type[6:]
        # bytes
        return super().set_value(new_value.value)

    def oh_post_update(self, data: bytes, img_type: Optional[str] = None):
        """Post an update to an openHAB image with new image data. Image type is automatically detected,
        in rare cases when this does not work it can be set manually.

        :param data: image data
        :param img_type: (optional) what kind of image, ``jpeg`` or ``png``
        """
        return super().oh_post_update(_convert_bytes(data, img_type))

    def oh_send_command(self, data: bytes, img_type: Optional[str] = None):
        """Send a command to an openHAB image with new image data. Image type is automatically detected,
        in rare cases when this does not work it can be set manually.

        :param data: image data
        :param img_type: (optional) what kind of image, ``jpeg`` or ``png``
        """
        return super().oh_send_command(_convert_bytes(data, img_type))
