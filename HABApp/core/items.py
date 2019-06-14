import typing

from .item import Item


class Items:
    def __init__(self):
        self.items = {}  # type: typing.Dict[str,Item]

    def item_exists(self, name) -> bool:
        return name in self.items

    def get_item(self, name) -> Item:
        return self.items[name]

    def get_items(self) -> typing.List[Item]:
        return list(self.items.values())

    def get_item_names(self) -> typing.List[str]:
        return list(self.items.keys())

    def set_state(self, name, new_state):
        try:
            self.items[name].set_state(new_state)
        except KeyError:
            item = Item(name)
            item.set_state(new_state)
            self.items[name] = item

    def set_item(self, item):
        assert isinstance(item, Item), type(item)
        self.items[item.name] = item

    def pop_item(self, name) -> Item:
        return self.items.pop(name)
