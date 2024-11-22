from collections.abc import Awaitable as __Awaitable
from collections.abc import Callable as __Callable
from typing import Any as __Any
from typing import Protocol as __Protocol
from typing import TypeAlias


TYPE_ANY_CLASS_TYPE: TypeAlias = type[object]
TYPE_FUNC_ASYNC: TypeAlias = __Callable[..., __Awaitable[__Any]]

TYPE_EVENT_CALLBACK: TypeAlias = __Callable[[__Any], __Any]


# noinspection PyPropertyDefinition
class HasNameAttr(__Protocol):
    @property
    def name(self) -> str:
        ...
