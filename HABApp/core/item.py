import datetime


class Item:
    def __init__(self, name: str):
        assert isinstance(name, str), type(name)

        self.name = name
        self.state = None

        _now = datetime.datetime.now()
        self.last_change: datetime.datetime = _now
        self.last_update: datetime.datetime = _now

    def set_state(self, new_state):
        # update timestamps
        _now = datetime.datetime.now()
        if self.state != new_state:
            self.last_change = _now
        self.last_update = _now

        self.state = new_state
        return None

    def get_state(self, default_value):
        if self.state is None:
            return default_value
        return self.state

    def __repr__(self):
        ret = ''
        for k in ['name', 'state', 'last_change', 'last_update']:
            ret += f'{"," if ret else ""} {k}: {getattr(self, k)}'
        return f'<{self.__class__.__name__} {ret:s}>'

    # only support == and != operators by default
    # __ne__ delegates to __eq__ and inverts the result so this is not overloaded separately
    def __eq__(self, other):
        return self.state == other

    def __bool__(self):
        return self.state
