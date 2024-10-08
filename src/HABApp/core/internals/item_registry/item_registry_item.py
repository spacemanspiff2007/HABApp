class ItemRegistryItem:
    """ItemRegistryItem, all items that will be stored in the Item Registry must inherit from this
    """

    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(**kwargs)
        if not isinstance(name, str):
            msg = f'Name must be a string not {type(name)}'
            raise TypeError(msg)
        self._name: str = name

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
