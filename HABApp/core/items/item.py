import datetime
import typing
import HABApp


class Item:

    @classmethod
    def get_item(cls, name: str):
        """Returns an already existing item. If it does not exist or has a different item type an exception will occur.

        :param name: Name of the item
        :return: the item
        """
        item = HABApp.core.Items.get_item(name)
        assert isinstance(item, cls), f'{cls} != {type(item)}'
        return item

    @classmethod
    def get_create_item(cls, name: str, default_state=None):
        """Creates a new item in HABApp and returns it or returns the already existing one with the given name

        :param name: item name
        :param default_state: state the item will have if it gets created
        :return: item
        """
        assert isinstance(name, str), type(name)

        try:
            item = HABApp.core.Items.get_item(name)
        except HABApp.core.Items.ItemNotFoundException:
            item = cls(name, default_state)
            HABApp.core.Items.set_item(item)

        assert isinstance(item, cls), f'{cls} != {type(item)}'
        return item

    def __init__(self, name: str, state=None):
        assert isinstance(name, str), type(name)

        self.name: str = name
        self.state: typing.Any = state

        _now = datetime.datetime.now()
        self.last_change: datetime.datetime = _now
        self.last_update: datetime.datetime = _now

    def set_state(self, new_state) -> bool:
        """Set a new state without creating events on the event bus

        :param new_state: new state
        :return: True if state has changed
        """
        state_changed = self.state != new_state

        _now = datetime.datetime.now()
        if state_changed:
            self.last_change = _now
        self.last_update = _now

        self.state = new_state
        return state_changed

    def post_state(self, new_state):
        """Set a new state and post appropriate events on the event bus (``ValueUpdateEvent``, ``ValueChangeEvent``)

        :param new_state: new state
        """
        old_state = self.state
        self.set_state(new_state)

        # create events
        HABApp.core.EventBus.post_event(self.name, HABApp.core.events.ValueUpdateEvent(self.name, new_state))
        if old_state != new_state:
            HABApp.core.EventBus.post_event(
                self.name, HABApp.core.events.ValueChangeEvent(self.name, value=new_state, old_value=old_state)
            )
        return None

    def get_state(self, default_value=None) -> typing.Any:
        """Return the state of the item.

        :param default_value: Return this value if the item state is None
        :return: State of the item
        """
        if self.state is None:
            return default_value
        return self.state

    def __repr__(self):
        ret = ''
        for k in ['name', 'state', 'last_change', 'last_update']:
            ret += f'{", " if ret else ""}{k}: {getattr(self, k)}'
        return f'<{self.__class__.__name__} {ret:s}>'

    # only support == and != operators by default
    # __ne__ delegates to __eq__ and inverts the result so this is not overloaded separately
    def __eq__(self, other):
        return self.state == other

    def __bool__(self):
        return bool(self.state)

    # rich comparisons only for numeric types (int and float)
    def __lt__(self, other):
        if not isinstance(self.state, (int, float)):
            return NotImplemented
        return self.state < other

    def __le__(self, other):
        if not isinstance(self.state, (int, float)):
            return NotImplemented
        return self.state <= other

    def __ge__(self, other):
        if not isinstance(self.state, (int, float)):
            return NotImplemented
        return self.state >= other

    def __gt__(self, other):
        if not isinstance(self.state, (int, float)):
            return NotImplemented
        return self.state > other
