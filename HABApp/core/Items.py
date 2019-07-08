import typing

from HABApp.core.items.item import Item as __Item


_ALL_ITEMS: typing.Dict[str, __Item] = {}


def item_exists(name: str) -> bool:
    return name in _ALL_ITEMS


def get_item(name: str) -> __Item:
    return _ALL_ITEMS[name]


def get_all_items() -> typing.List[__Item]:
    return list(_ALL_ITEMS.values())


def get_item_names() -> typing.List[str]:
    return list(_ALL_ITEMS.keys())


def create_item(name: str, item_factory, item_state=None) -> __Item:
    assert issubclass(item_factory, __Item), item_factory
    _ALL_ITEMS[name] = new_item = item_factory(name, state=item_state)
    return new_item


def set_item(item: __Item):
    assert isinstance(item, __Item), type(item)
    _ALL_ITEMS[item.name] = item


def pop_item(name: str) -> __Item:
    return _ALL_ITEMS.pop(name)
