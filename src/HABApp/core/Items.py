import typing

from HABApp.core.items.base_item import BaseItem as __BaseItem

_ALL_ITEMS: typing.Dict[str, __BaseItem] = {}


class ItemNotFoundException(Exception):
    def __init__(self, name: str):
        super().__init__(f'Item {name} does not exist!')
        self.name: str = name


class ItemAlreadyExistsError(Exception):
    def __init__(self, name: str):
        super().__init__(f'Item {name} does already exist and can not be added again!')
        self.name: str = name


def item_exists(name: str) -> bool:
    return name in _ALL_ITEMS


def get_item(name: str) -> __BaseItem:
    try:
        return _ALL_ITEMS[name]
    except KeyError:
        raise ItemNotFoundException(name) from None


def get_all_items() -> typing.List[__BaseItem]:
    return list(_ALL_ITEMS.values())


def get_all_item_names() -> typing.List[str]:
    return list(_ALL_ITEMS.keys())


def create_item(name: str, item_factory, initial_value=None) -> __BaseItem:
    assert issubclass(item_factory, __BaseItem), item_factory
    new_item = item_factory(name, initial_value=initial_value)
    add_item(new_item)
    return new_item


def add_item(item: __BaseItem):
    assert isinstance(item, __BaseItem), type(item)
    name = item.name

    existing = _ALL_ITEMS.get(name)
    if existing is not None:
        # adding the same item multiple times will not cause an exception
        if existing is item:
            return None

        # adding a new item with the same name raises an exception
        raise ItemAlreadyExistsError(name)

    _ALL_ITEMS[name] = item
    item._on_item_add()


def pop_item(name: str) -> __BaseItem:
    try:
        item = _ALL_ITEMS.pop(name)
    except KeyError:
        raise ItemNotFoundException(name) from None

    item._on_item_remove()
    return item
