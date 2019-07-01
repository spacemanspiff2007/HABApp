import typing

from .item import Item


_ALL_ITEMS: typing.Dict[str, Item] = {}


def item_exists(name) -> bool:
    return name in _ALL_ITEMS


def get_item(name) -> Item:
    return _ALL_ITEMS[name]


def get_all_items() -> typing.List[Item]:
    return list(_ALL_ITEMS.values())


def get_item_names() -> typing.List[str]:
    return list(_ALL_ITEMS.keys())


def set_item_state(name, new_state):
    try:
        _ALL_ITEMS[name].set_state(new_state)
    except KeyError:
        item = Item(name)
        item.set_state(new_state)
        _ALL_ITEMS[name] = item


def set_item(item):
    assert isinstance(item, Item), type(item)
    _ALL_ITEMS[item.name] = item


def pop_item(name) -> Item:
    return _ALL_ITEMS.pop(name)
