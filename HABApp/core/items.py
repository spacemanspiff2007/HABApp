import datetime
import logging
import typing

if typing.TYPE_CHECKING:
    pass

log = logging.getLogger('HABApp.Items')


class Item:
    def __init__(self, name: str):
        assert isinstance(name, str), type(name)

        self.name = name
        self.state = None

        _now = datetime.datetime.now()
        self.last_change: datetime.datetime = _now
        self.last_update: datetime.datetime = _now

    def set_state(self, new_state):
        _now = datetime.datetime.now()
        if self.state != new_state:
            self.last_change = _now
        self.last_update = _now
        self.state = new_state

    def __repr__(self):
        ret = ''
        for k in ['name', 'state', 'last_change', 'last_update']:
            ret += f'{"," if ret else ""} {k}: {getattr(self, k)}'
        return f'<{self.__class__.__name__}{ret:s}>'


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
