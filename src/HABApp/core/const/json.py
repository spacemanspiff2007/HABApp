try:
    import ujson
    load_json = ujson.loads
    dump_json = ujson.dumps
except ImportError:
    import json
    load_json = json.loads
    dump_json = json.dumps
