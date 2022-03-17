import sys
from typing import Dict, List, Optional

from HABApp.core.errors import ProxyObjHasNotBeenReplacedError

PROXIES: List['ProxyObj'] = []


class RestoreableObj:
    def __init__(self, key: str, globals: dict, proxy: 'ProxyObj'):
        self.key = key
        self.globals = globals
        self.proxy = proxy

    def restore(self):
        self.globals[self.key] = self.proxy
        self.globals = None
        self.key = None
        self.proxy = None


class ProxyObj:
    def __init__(self, to_replace: callable, globals: dict):
        self.to_replace: Optional[callable] = to_replace
        self.globals: Optional[dict] = globals

        PROXIES.append(self)

    @property
    def to_replace_name(self) -> str:
        return str(getattr(self.to_replace, "__name__", self.to_replace))

    def __getattr__(self, item):
        raise ProxyObjHasNotBeenReplacedError(self)

    def __call__(self, *args, **kwargs):
        raise ProxyObjHasNotBeenReplacedError(self)

    def __str__(self):
        return f'<{self.__class__.__name__} {self.to_replace_name}>'

    def replace(self, replacements: Dict[object, object], final: bool):
        assert self.globals is not None
        replacement = replacements[self.to_replace]

        for name, value in self.globals.items():
            if value is self:
                self.globals[name] = replacement
                if not final:
                    return RestoreableObj(name, self.globals, self)
                break
        else:
            file = self.globals.get('__file__', '?')
            raise ValueError(f'"{self.to_replace_name}" should be replaced but was not found in {file}!')

        self.globals = None
        self.to_replace = None


def create_proxy(to_replace: callable) -> ProxyObj:
    frm = sys._getframe(2)
    return ProxyObj(to_replace, frm.f_globals)


def replace_proxies(replacements: Dict[object, object], final: bool) -> List[RestoreableObj]:
    restore_objs = []
    for proxy in PROXIES:
        restore = proxy.replace(replacements, final)
        if restore is not None:
            restore_objs.append(restore)

    if not final:
        return restore_objs

    PROXIES.clear()
    return []