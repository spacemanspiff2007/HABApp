import logging
from typing import Dict, Any, Final, TypeVar, Tuple, Generic


T = TypeVar('T')

log = logging.getLogger('HABApp.openhab.transform')


class TransformationFactoryBase(Generic[T]):
    def __init__(self, registry: 'TransformationRegistryBase'):
        self._registry: Final = registry

    def __repr__(self):
        return f'<{self._registry.name.title()}{self.__class__.__name__}>'

    def __getitem__(self, key: str) -> T:
        return self._registry.get(key)


def sort_order(uid: str):
    # created through file
    if '.' in uid:
        name, ext = uid.rsplit('.', 1)
        return 0, ext, name

    # UI created
    return 1, uid.split(':')


class TransformationRegistryBase:
    objs: Dict[str, Any]

    def __init__(self, name: str):
        self.name: Final = name

    def __repr__(self):
        return f'<{self.__class__.__name__} {" ".join(self.available())}'

    def available(self) -> Tuple[str, ...]:
        return tuple(sorted(self.objs.keys(), key=sort_order))

    def get(self, name: str):
        raise NotImplementedError()

    def set(self, name: str, configuration: dict):
        raise NotImplementedError()

    def clear(self):
        self.objs.clear()
