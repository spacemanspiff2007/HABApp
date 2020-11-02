import typing

from .base_event import OpenhabEvent

# smarthome/things/NAME/state -> 17
# openhab/things/NAME/state   -> 15
# todo: revert this once we go OH3 only
NAME_START: int = 15


class ThingStatusInfoEvent(OpenhabEvent):
    def __init__(self, name: str = '', status: str = '', detail: str = ''):
        super().__init__()

        self.name: str = name
        self.status: str = status
        self.detail: str = detail

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # smarthome/things/chromecast:chromecast:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/status
        return cls(name=topic[NAME_START:-7], status=payload['status'], detail=payload['statusDetail'])

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, status: {self.status}, detail: {self.detail}>'


class ThingStatusInfoChangedEvent(OpenhabEvent):
    def __init__(self, name: str = '', status: str = '', detail: str = '', old_status: str = '', old_detail: str = ''):
        super().__init__()

        self.name: str = name
        self.status: str = status
        self.detail: str = detail
        self.old_status: str = old_status
        self.old_detail: str = old_detail

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # smarthome/things/chromecast:chromecast:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/statuschanged
        name = topic[NAME_START:-14]
        new, old = payload
        return cls(
            name=name, status=new['status'], detail=new['statusDetail'],
            old_status=old['status'], old_detail=old['statusDetail']
        )

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, ' \
               f'status: {self.status}, detail: {self.detail}, ' \
               f'old_status: {self.old_status}, old_detail: {self.old_detail}>'


class ThingConfigStatusInfoEvent(OpenhabEvent):
    def __init__(self, name: str = '', messages: typing.List[typing.Dict[str, str]] = [{}]):
        super().__init__()

        self.name: str = name
        self.messages: typing.List[typing.Dict[str, str]] = messages

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # 'smarthome/things/zwave:device:controller:my_node/config/status'
        return cls(name=topic[NAME_START:-14], messages=payload['configStatusMessages'])

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, messages: {self.messages}>'


class ThingFirmwareStatusInfoEvent(OpenhabEvent):
    def __init__(self, name: str = '', status: str = ''):
        super().__init__()
        self.name: str = name
        self.status: str = status

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # 'smarthome/things/zwave:device:controller:my_node/firmware/status'
        return cls(name=topic[NAME_START:-16], status=payload['firmwareStatus'])

    def __repr__(self):
        return f'<{self.__class__.__name__} status: {self.status}>'
