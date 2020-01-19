from .base_event import OpenhabEvent


class ThingStatusInfoEvent(OpenhabEvent):
    def __init__(self, _in_dict):
        # Hack for NONE types, todo: find proper solution
        _in_dict['payload'] = _in_dict['payload'].replace('"NONE"', 'null')
        super().__init__(_in_dict)

        # smarthome/things/chromecast:chromecast:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/status
        self.name: str = self._topic[17:-7]
        self.status: str = self._payload['status']
        self.detail: str = self._payload['statusDetail']

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, status: {self.status}, detail: {self.detail}>'


class ThingStatusInfoChangedEvent(OpenhabEvent):
    def __init__(self, _in_dict):
        # Hack for NONE types, todo: find proper solution
        _in_dict['payload'] = _in_dict['payload'].replace('"NONE"', 'null')
        super().__init__(_in_dict)

        # smarthome/things/chromecast:chromecast:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/statuschanged
        self.name: str = self._topic[17:-14]
        self.status: str = self._payload[0]['status']
        self.detail: str = self._payload[0]['statusDetail']
        self.old_status: str = self._payload[1]['status']
        self.old_detail: str = self._payload[1]['statusDetail']

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, ' \
               f'status: {self.status}, detail: {self.detail}, ' \
               f'old_status: {self.old_status}, old_detail: {self.old_detail}>'
