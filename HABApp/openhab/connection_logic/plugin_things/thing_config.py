import re
import typing

import bidict

from HABApp.core.habapp_logger import log_error
from HABApp.openhab.connection_handler.func_async import async_set_thing_cfg
from ._log import log_cfg as log


class ThingConfigChanger:
    zw_param = re.compile(r'config_(?P<p>\d+)_(?P<w>\d+)(?:_\w+)?')
    zw_group = re.compile(r'group_(\d+)')

    @classmethod
    def from_dict(cls, uid: str, _in: dict) -> 'ThingConfigChanger':
        c = cls(uid)
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

    def __init__(self, uid: str):
        self.uid: str = uid
        self.alias = bidict.bidict()
        self.org: typing.Dict[str, typing.Any] = {}
        self.new: typing.Dict[str, typing.Any] = {}

    def __getitem__(self, key):
        return self.org[self.alias.get(key, key)]

    def __setitem__(self, o_key, item):
        key = self.alias.get(o_key, o_key)
        if key not in self.org:
            raise KeyError(f'Parameter "{o_key}" does not exist for {self.uid}!')
        if item == self.org[key]:
            return None
        self.new[key] = item

    def __contains__(self, key):
        return self.alias.get(key, key) in self.org

    def get(self, key, default=None):
        try:
            return self.org[self.alias.get(key, key)]
        except KeyError:
            return default

    def keys(self):
        return (self.alias.inverse.get(k, k) for k in self.org.keys())

    def values(self):
        return self.org.values()

    def get_dict(self, filter=False, new=False):
        r = {}
        for k, v in (self.org if not new else self.new).items():
            if filter and (k.startswith('action_') or k in ('node_id', 'wakeup_node')):
                continue
            k = self.alias.inverse.get(k, k)
            r[k] = v
        return r

    async def update_thing_cfg(self):
        if not self.new:
            log.debug(f'Config of {self.uid} is already correct!')
            return None

        try:
            # we write only the changed configuration
            ret = await async_set_thing_cfg(self.uid, cfg=self.new)
            if ret is None:
                return None
        except Exception as e:
            log_error(log, f'Could not set new config for {self.uid}: {e}')
            return None

        log.info(f'Config of {self.uid} successfully updated!')
