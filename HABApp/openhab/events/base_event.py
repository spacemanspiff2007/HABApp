import datetime
import ujson

class BaseItemEvent:
    def __init__(self, _in_dict : dict):
        assert isinstance(_in_dict, dict), type(_in_dict)
        self._topic   = _in_dict['topic']
        self._type    = _in_dict['type']
        self._payload = ujson.loads(_in_dict['payload'])
