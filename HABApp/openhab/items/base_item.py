from HABApp.core.items.base_valueitem import BaseValueItem
from HABApp.openhab import get_openhab_interface


class OpenhabItem(BaseValueItem):
    """Base class for items which exists in OpenHAB.
    """
