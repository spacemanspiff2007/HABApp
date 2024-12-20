from typing import Any, Final

from javaproperties import loads as load_map_file

from HABApp.openhab.errors import MapTransformationNotFound
from HABApp.openhab.transformations._map.classes import MapTransformation, MapTransformationWithDefault
from HABApp.openhab.transformations.base import TransformationFactoryBase, TransformationRegistryBase, log


class MapTransformationRegistry(TransformationRegistryBase):

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.objs: dict[str, tuple[dict, Any]] = {}

    def get(self, name: str) -> MapTransformation | MapTransformationWithDefault:
        try:
            data, default = self.objs[name]
        except KeyError:
            raise MapTransformationNotFound(f'Map transformation "{name:s}" not found!') from None

        if default:
            return MapTransformationWithDefault(data, name=name, default=default)
        else:
            return MapTransformation(data, name=name)

    def set(self, name: str, configuration: dict[str, str]):
        data = load_map_file(configuration['function'])
        if not data:
            log.warning(f'Map transformation "{name:s}" is empty -> skipped!')
            return None

        default = data.pop('', None)
        map_keys = all(k.isdecimal() for k in data)
        map_values = all(v.isdecimal() for v in data.values())
        if map_values and default is not None and default.isdecimal():
            default = int(default)

        obj = {}
        for k, v in data.items():
            key = k if not map_keys else int(k)
            value = v if not map_values else int(v)
            obj[key] = value

        self.objs[name] = obj, default


MAP_REGISTRY: Final = MapTransformationRegistry('map')


class MapTransformationFactory(TransformationFactoryBase[dict[str | int, str | int]]):
    pass


MAP_FACTORY = MapTransformationFactory(MAP_REGISTRY)
