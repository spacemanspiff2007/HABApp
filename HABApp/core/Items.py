import typing

from HABApp.core.items.base import BaseItem as __BaseItem


_ALL_ITEMS: typing.Dict[str, __BaseItem] = {}


class ItemNotFoundException(Exception):
    pass


def item_exists(name: str) -> bool:
    return name in _ALL_ITEMS


def get_item(name: str) -> __BaseItem:
    try:
        return _ALL_ITEMS[name]
    except KeyError:
        raise ItemNotFoundException(f'Item {name} does not exist!')


def get_all_items() -> typing.List[__BaseItem]:
    return list(_ALL_ITEMS.values())


def get_all_item_names() -> typing.List[str]:
    return list(_ALL_ITEMS.keys())


def create_item(name: str, item_factory, initial_value=None) -> __BaseItem:
    assert issubclass(item_factory, __BaseItem), item_factory
    _ALL_ITEMS[name] = new_item = item_factory(name, initial_value=initial_value)
    return new_item


def set_item(item: __BaseItem):
    assert isinstance(item, __BaseItem), type(item)
    _ALL_ITEMS[item.name] = item


def pop_item(name: str) -> __BaseItem:
    return _ALL_ITEMS.pop(name)
