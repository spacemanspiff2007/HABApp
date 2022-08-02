from typing import Any as __Any
from typing import Awaitable as __Awaitable
from typing import Callable as __Callable
from typing import Type as __Type

from .const import PYTHON_310 as __IS_GE_PYTHON_310

if __IS_GE_PYTHON_310:
    from typing import TypeAlias
else:
    from typing import Final as TypeAlias

HINT_ANY_CLASS: TypeAlias = __Type[object]
HINT_FUNC_ASYNC: TypeAlias = __Callable[..., __Awaitable[__Any]]

HINT_EVENT_CALLBACK: TypeAlias = __Callable[[__Any], __Any]
