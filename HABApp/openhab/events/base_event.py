import ujson


class BaseItemEvent:
    def __init__(self, _in_dict: dict):
        super().__init__()
        assert isinstance(_in_dict, dict), type(_in_dict)
        self._topic = _in_dict['topic']
        self._type = _in_dict['type']
        self._payload = ujson.loads(_in_dict['payload'])

    def __repr__(self):
        return f'<{self.__class__.__name__} _topic: {self._topic} _type: {self._type}, _payload: {self._payload}>'
