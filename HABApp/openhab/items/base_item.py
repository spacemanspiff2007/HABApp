from HABApp.core.items.base_value import BaseValueItem


class OpenhabItem(BaseValueItem):
    """Item which exists in OpenHAB.

    :ivar str ~.name: Name of the item (read only)
    :ivar ~.value: Value of the item, can be anything (read only)
    :ivar ~.datetime.datetime last_change: Timestamp of the last time when the item has changed the value (read only)
    :ivar ~.datetime.datetime last_update: Timestamp of the last time when the item has updated the value (read only)
    """
