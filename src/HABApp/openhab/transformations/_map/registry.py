from typing import Final

from fastnumbers import check_intlike
from fastnumbers import int as to_int
from immutables import Map
from javaproperties import loads as load_map_file

from HABApp.openhab.errors import MapTransformationNotFound
from HABApp.openhab.transformations._map.classes import MapTransformation, MapTransformationWithDefault
from HABApp.openhab.transformations.base import TransformationFactoryBase, TransformationRegistryBase, log


class MapTransformationRegistry(TransformationRegistryBase):

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.objs: dict[str, tuple[Map[str | int, str | int], str | int]] = {}

    def get(self, name: str) -> MapTransformation | MapTransformationWithDefault:
        try:
            data, default = self.objs[name]
        except KeyError:
            msg = f'Map transformation "{name:s}" not found!'
            raise MapTransformationNotFound(msg) from None

        if default is not None:
            return MapTransformationWithDefault(data, name=name, default=default)

        return MapTransformation(data, name=name)

    def set(self, name: str, configuration: dict[str, str]) -> None:

        if not (data := load_map_file(configuration['function'])):
            log.warning(f'Map transformation "{name:s}" is empty -> skipped!')
            return None

        default = data.pop('', None)
        if default is not None and check_intlike(default):
            default = to_int(default)

        map_keys = all(check_intlike(k) for k in data)
        map_values = all(check_intlike(v) for v in data.values())

        obj = {}
        for k, v in data.items():
            key = k if not map_keys else to_int(k)
            value = v if not map_values else to_int(v)
            obj[key] = value

        self.objs[name] = Map(obj), default


MAP_REGISTRY: Final = MapTransformationRegistry('map')


class MapTransformationFactory(TransformationFactoryBase[dict[str | int, str | int]]):
    pass


MAP_FACTORY = MapTransformationFactory(MAP_REGISTRY)
