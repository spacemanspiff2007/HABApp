class ItemRegistryItem:
    """ItemRegistryItem, all items that will be stored in the Item Registry must inherit from this
    """

    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        assert isinstance(name, str), type(name)
        self._name: str = name

    @property
    def name(self) -> str:
        """
        :return: Name of the item (read only)
        """
        return self._name

    def _on_item_added(self):
        """This function gets automatically called when the item was added to the item registry
        """
        raise NotImplementedError()

    def _on_item_removed(self):
        """This function gets automatically called when the item was removed from the item registry
        """
        raise NotImplementedError()
