import typing as _typing

# noinspection PyPep8Naming, PyShadowingBuiltins
from ._map import MAP_FACTORY as map

if _typing.TYPE_CHECKING:
    map = map
