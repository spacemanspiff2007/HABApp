from typing import Any as __Any
from typing import Callable as __Callable
from typing import Type as __Type

TYPE_ANY_CLASS = __Type[object]

TYPE_EVENT_CALLBACK = __Callable[[__Any], __Any]

TYPE_SCHEDULER_CALLBACK = __Callable[[], __Any]
