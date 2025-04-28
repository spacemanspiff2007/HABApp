from collections.abc import Mapping
from typing import Final, NoReturn, TypeAlias

from HABApp.openhab.errors import MapTransformationError


MapKeyType: TypeAlias = int | str
MapValueType: TypeAlias = int | str


class MapTransformation(dict[MapKeyType, MapValueType]):
    def __init__(self, obj: Mapping[MapKeyType, MapValueType], *, name: str) -> None:
        super().__init__(obj)
        self._name: Final = name

    def __repr__(self, additional: str = '') -> str:
        return f'<{self.__class__.__name__} name={self._name} items={super().__repr__()}{additional:s}>'


class MapTransformationWithDefault(MapTransformation):
    def __init__(self, obj: Mapping[MapKeyType, MapValueType], *, default: MapValueType, name: str) -> None:
        super().__init__(obj, name=name)
        self._default: Final = default

    def __missing__(self, key: MapKeyType) -> int | str:
        return self._default

    def __repr__(self, additional: str = '') -> str:
        return super().__repr__(f', default={self._default}{additional}')

    def get(self, key: MapKeyType, default: MapValueType | None = None) -> NoReturn:  # noqa: ARG002
        msg = f'Mapping is already defined with a default: "{self._default}"'
        raise MapTransformationError(msg)
