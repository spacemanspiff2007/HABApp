from typing import Any as __Any
from typing import Awaitable as __Awaitable
from typing import Callable as __Callable
from typing import Type as __Type

from .const import PYTHON_310 as __IS_GE_PYTHON_310


if __IS_GE_PYTHON_310:
    from typing import TypeAlias
else:
    from typing import Final as TypeAlias


TYPE_ANY_CLASS_TYPE: TypeAlias = __Type[object]
TYPE_FUNC_ASYNC: TypeAlias = __Callable[..., __Awaitable[__Any]]

TYPE_EVENT_CALLBACK: TypeAlias = __Callable[[__Any], __Any]
