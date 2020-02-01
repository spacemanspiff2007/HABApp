from HABApp.openhab.items.base_item import OpenhabItem
from ..definitions import RawValue
from HABApp.openhab import get_openhab_interface
import typing
from base64 import b64encode


class ImageItem(OpenhabItem):
    """ImageItem which accepts and converts the data types from OpenHAB"""

    def __init__(self, name: str, initial_value=None):
        super().__init__(name, initial_value)

        # this item is unique because we also save the image type and thus have two states
        self.image_type: typing.Optional[str] = None

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

    def post_update(self, img_type: str, data: bytes):
        """Post an update to an openhab image with new image data

        :param img_type: what kind of image, ``jpeg`` or ``png``
        :param data: image data
        """
        assert isinstance(data, bytes), type(data)
        assert img_type in ('jpeg', 'png'), f'"{img_type}"'

        state = f'data:image/{img_type};base64,{b64encode(data).decode("ascii")}'
        get_openhab_interface().post_update(self.name, state)
        return None
