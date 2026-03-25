from typing import Any, Final

from HABApp.core.errors import ItemNameNotOfTypeStrError


class ItemRegistryItem:
    """ItemRegistryItem, all items that will be stored in the Item Registry must inherit from this
    """

    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        if not isinstance(name, str):
            raise ItemNameNotOfTypeStrError.from_value(name)

        self._name: Final = name

    @property
    def name(self) -> str:
        """
        :return: Name of the item (read only)
        """
        return self._name

    def _on_item_added(self) -> None:
        """This function gets automatically called when the item was added to the item registry
        """
        raise NotImplementedError()

    def _on_item_removed(self) -> None:
        """This function gets automatically called when the item was removed from the item registry
        """
        raise NotImplementedError()
