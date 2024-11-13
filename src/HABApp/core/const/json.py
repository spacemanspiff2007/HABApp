from collections.abc import Callable
from typing import Any


try:
    import ujson
    load_json: Callable[[str], Any] = ujson.loads
    dump_json: Callable[[str], Any] = ujson.dumps
except ImportError:
    import json
    load_json: Callable[[str], Any] = json.loads
    dump_json: Callable[[str], Any] = json.dumps
