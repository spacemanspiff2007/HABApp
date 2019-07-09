import datetime
import typing


class Item:
    def __init__(self, name: str, state=None):
        assert isinstance(name, str), type(name)

        self.name: str = name
        self.state: typing.Any = state

        _now = datetime.datetime.now()
        self.last_change: datetime.datetime = _now
        self.last_update: datetime.datetime = _now

    def set_state(self, new_state) -> bool:
        """Set a new state without creating events

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
        return self.state

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
