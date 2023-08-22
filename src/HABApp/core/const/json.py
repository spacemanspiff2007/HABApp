from typing import Any, Callable

import msgspec

try:
    import ujson
    load_json: Callable[[str], Any] = ujson.loads
    dump_json: Callable[[str], Any] = ujson.dumps
except ImportError:
    import json
    load_json: Callable[[str], Any] = json.loads
    dump_json: Callable[[str], Any] = json.dumps


decode_struct = msgspec.json.decode
encode_struct = msgspec.json.encode
