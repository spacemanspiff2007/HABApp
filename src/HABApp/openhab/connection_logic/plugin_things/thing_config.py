import re
import typing

import bidict

from HABApp.core.logger import log_error
from HABApp.openhab.connection_handler.func_async import async_set_thing_cfg
from ._log import log_cfg as log


def ensure_same_types(key: str, org, val):
    t_org = type(org)
    t_val = type(val)
    if t_org is t_val:
        return None

    _a = str(t_org)
    _a = _a[7:-1] if _a.startswith('<class ') and _a[-1] == '>' else _a

    _b = str(t_val)
    _b = _b[7:-1] if _b.startswith('<class ') and _b[-1] == '>' else _b
    raise ValueError(f"Datatype of parameter '{key}' must be {_a} but is {_b}: '{val}'")


re_ref = re.compile(r'\$(\w+)')


class ThingConfigChanger:
    zw_param = re.compile(r'config_(?P<param>\d+)_(?P<width>\d+)(?P<bitmask>_\w+)?')
    zw_group = re.compile(r'group_(\d+)')

    @classmethod
    def from_dict(cls, uid: str, _in: dict) -> 'ThingConfigChanger':
        c = cls(uid)
        c.org = _in
        for k in _in:
            # Z-Wave Params -> 0
            m = ThingConfigChanger.zw_param.fullmatch(k)
            if m:
                # check if the entry without bitmask is also in the cfg dict because then we use this entry
                # and split up the bitmask entries accordingly
                # 154 -> config_154_4
                # 154_000000FF -> config_154_4_000000FF
                if m.group(3) is not None:
                    if f'config_{m.group(1)}_{m.group(2)}' in _in:
                        c.alias[f'{m.group(1)}{m.group(3)}'] = k
                        continue

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
        self.alias: bidict.bidict[typing.Union[str, int], str] = bidict.bidict()
        self.org: typing.Dict[str, typing.Any] = {}
        self.new: typing.Dict[str, typing.Any] = {}

    def __getitem__(self, key):
        return self.org[self.alias.get(key, key)]

    def __setitem__(self, o_key, value):
        key = self.alias.get(o_key, o_key)
        if key not in self.org:
            raise KeyError(f'Parameter "{o_key}" does not exist for {self.uid}!')

        # Make it possible to substitue refs with $1
        if isinstance(value, str) and '$' in value:
            o_value = value
            refs = re_ref.findall(o_value)
            # Since we use str.replace we need to start with the longest refs!
            for ref in sorted(refs, key=len, reverse=True):
                try:
                    _ref_key = int(ref)
                except ValueError:
                    _ref_key = ref
                _ref_key = self.alias.get(_ref_key, _ref_key)

                try:
                    _ref_val = self.new.get(_ref_key, self.org[_ref_key])
                except KeyError:
                    raise KeyError(f'Reference "{ref}" in "{o_value}" does not exist for {self.uid}!') from None

                value = value.replace(f'${ref}', str(_ref_val))

            log.debug(f'Evaluating "{value}"')
            value = eval(value, {}, {})
            log.debug(f' -> "{value}"')

        org = self.org[key]
        ensure_same_types(o_key, org, value)

        if value == org:
            return None
        self.new[key] = value

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
