from typing import Callable, List

from EasyCo import ConfigEntry

import HABApp


class DummyConfigSection:
    def __init__(self, key: str, notify: list):
        self.dummy_key: str = key
        self.dummy_notify: List[Callable] = notify.copy()

    def notify_change(self):
        for k in self.dummy_notify:
            k()


DUMMY_VALUES = {
    'location.latitude': 52.5185537,
    'location.longitude': 13.3758636,
    'location.elevation': 43,
}


def __copy_to_obj(obj, cfg, stack: tuple, used_dummies: set):

    for name in getattr(cfg, '_ConfigContainer__containers'):
        child = DummyConfigSection(name, getattr(cfg, '_ConfigContainer__notify'))
        setattr(obj, name, child)
        new_stack = stack + (name,)
        __copy_to_obj(child, getattr(cfg, name), new_stack, used_dummies)

    for name in getattr(cfg, '_ConfigContainer__entries'):
        dummy_key = '.'.join(stack + (name,))
        value = DUMMY_VALUES.get(dummy_key)
        if value is not None:
            used_dummies.add(dummy_key)
        else:
            entry = getattr(cfg, name)
            value = entry.default if isinstance(entry, ConfigEntry) else entry
        setattr(obj, name, value)


def get_dummy_cfg():
    obj = DummyConfigSection('root', getattr(HABApp.config.config.CONFIG, '_ConfigContainer__notify'))
    used = set()
    __copy_to_obj(obj, HABApp.config.config.CONFIG, tuple(), used)

    not_used = set(DUMMY_VALUES.keys()) - used
    assert not not_used, not_used

    return obj
