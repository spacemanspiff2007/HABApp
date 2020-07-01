import bidict
import re
import typing


class ThingConfigChanger:
    zw_param = re.compile(r'config_(?P<p>\d+)_(?P<w>\d+)(?:_\w+)?')
    zw_group = re.compile(r'group_(\d+)')

    @classmethod
    def from_dict(cls, _in: dict) -> 'ThingConfigChanger':
        c = cls()
        c.org = _in
        for k in _in:
            # Z-Wave Params -> 0
            m = ThingConfigChanger.zw_param.fullmatch(k)
            if m:
                c.alias[int(m.group(1))] = k
                continue

            # Z-Wave Groups to Group1
            m = ThingConfigChanger.zw_group.fullmatch(k)
            if m:
                c.alias[f'Group{m.group(1)}'] = k
                continue
        return c

    def __init__(self):
        self.alias = bidict.bidict()
        self.org: typing.Dict[str, typing.Any] = {}
        self.new: typing.Dict[str, typing.Any] = {}

    def __getitem__(self, key):
        return self.org[self.alias.get(key, key)]

    def __setitem__(self, key, item):
        self.new[self.alias.get(key, key)] = item

    def __contains__(self, key):
        return self.alias.get(key, key) in self.org

    def keys(self):
        return (self.alias.inverse.get(k, k) for k in self.org.keys())

    def values(self):
        return self.org.values()

    def items(self):
        for k, v in zip(self.keys(), self.values()):
            yield k, v
