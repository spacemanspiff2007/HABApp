# noinspection PyProtectedMember
from collections.abc import Callable
from sys import _getframe as sys_get_frame
from typing import Final

from HABApp.core.errors import ProxyObjHasNotBeenReplacedError


PROXIES: list['StartUpProxyObj'] = []


class ProxyObjBase:
    @property
    def to_replace_name(self) -> str:
        raise NotImplementedError()

    def __getattr__(self, item):
        raise ProxyObjHasNotBeenReplacedError(self)

    def __call__(self, *args, **kwargs):
        raise ProxyObjHasNotBeenReplacedError(self)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.to_replace_name}>'


class ConstProxyObj(ProxyObjBase):
    def __init__(self, name: str) -> None:
        self.name: Final = name

    @property
    def to_replace_name(self) -> str:
        return self.name


class StartUpProxyObj(ProxyObjBase):
    def __init__(self, to_replace: Callable, globals: dict) -> None:
        self.to_replace: Callable | None = to_replace
        self.globals: dict | None = globals

        PROXIES.append(self)

    @property
    def to_replace_name(self) -> str:
        return str(getattr(self.to_replace, '__name__', self.to_replace))

    def replace(self, replacements: dict[object, object], final: bool):
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
            msg = f'"{self.to_replace_name}" should be replaced but was not found in {file}!'
            raise ValueError(msg)

        self.globals = None
        self.to_replace = None


def create_proxy(to_replace: Callable) -> StartUpProxyObj:
    frm = sys_get_frame(2)
    return StartUpProxyObj(to_replace, frm.f_globals)


class RestoreableObj:
    def __init__(self, key: str, globals: dict, proxy: 'StartUpProxyObj') -> None:
        self.key = key
        self.globals = globals
        self.proxy = proxy

    def restore(self) -> None:
        self.globals[self.key] = self.proxy
        self.globals = None
        self.key = None
        self.proxy = None


def replace_proxies(replacements: dict[object, object], final: bool) -> list[RestoreableObj]:
    restore_objs = []
    for proxy in PROXIES:
        restore = proxy.replace(replacements, final)
        if restore is not None:
            restore_objs.append(restore)

    if not final:
        return restore_objs

    PROXIES.clear()
    return []
