import pathlib

from voluptuous import Required, Coerce, Optional


class ConfigEntry:
    def __init__(self):
        self._entry_is_required = True
        self._entry_name = self.__class__.__name__.lower()
        self._entry_kwargs = {}
        self._entry_validators = {}
        self._entry_notify_on_change = []

    def subscribe_for_changes(self, callback):
        assert callback not in self._entry_notify_on_change
        self._entry_notify_on_change.append(callback)

    def iter_entry(self):
        for name, value in self.__dict__.items():
            assert name.islower(), f'variable name must be lower case! "{name}"'
            if name.startswith('_entry_'):
                continue
            yield name, value

    def update_schema(self, _dict):

        val = {}
        for name, value in self.iter_entry():

            # datatype
            if name in self._entry_validators:
                _type = self._entry_validators[name]
            else:
                _type = type(value)
                if _type is int or _type is float:
                    _type = Coerce(_type)

                # we do not load Path objects, we load the strings
                if isinstance(value, pathlib.Path):
                    _type = str

            # name
            __name = {'schema' : name}
            __name.update(self._entry_kwargs.get(name, {}))
            val[Required(**__name)] = _type

        _dict[ Required(self._entry_name) if self._entry_is_required else Optional(self._entry_name)] = val
        return _dict

    def insert_data(self, _dict):
        _insert = {}
        for name, value in self.iter_entry():
            _insert[name] = value
        _dict[self._entry_name] = _insert

    def load_data(self, _dict):
        if self._entry_name not in _dict:
            return None

        notify = False
        _dict = _dict[self._entry_name]
        for name, value in self.iter_entry():
            cur = getattr(self, name)
            new = _dict[name]
            if cur != new:
                notify = True
            setattr(self, name, new)

        if notify:
            for cb in self._entry_notify_on_change:
                cb()


class ConfigEntryContainer:

    def iter_entriy(self):
        for name, value in self.__dict__.items():
            if not isinstance(value, ConfigEntry):
                continue
            yield name, value

    def insert_data(self, _dict):
        _insert = {}
        for name, value in self.iter_entriy():
            value.insert_data(_insert)
        _dict[self.__class__.__name__.lower()] = _insert

    def load_data(self, _dict):
        _load = _dict[self.__class__.__name__.lower()]
        for name, value in self.iter_entriy():
            value.load_data(_load)

    def update_schema(self, _dict):
        schema = {}
        for name, value in self.iter_entriy():
            value.update_schema(schema)
        _dict[Required(self.__class__.__name__.lower())] = schema
