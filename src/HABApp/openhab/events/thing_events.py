from typing import List, Dict, Any, Final

from .base_event import OpenhabEvent
from ..definitions import ThingStatusEnum, ThingStatusDetailEnum
from ..definitions.things import THING_STATUS_DEFAULT, THING_STATUS_DETAIL_DEFAULT


class ThingStatusInfoEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar ThingStatusEnum status:
    :ivar ThingStatusDetailEnum detail:
    :ivar str description:
    """
    name: str
    status: ThingStatusEnum
    detail: ThingStatusDetailEnum
    description: str

    def __init__(self, name: str = '', status: ThingStatusEnum = THING_STATUS_DEFAULT,
                 detail: ThingStatusDetailEnum = THING_STATUS_DETAIL_DEFAULT, description: str = ''):
        super().__init__()

        self.name: Final = name
        self.status: Final = status
        self.detail: Final = detail
        self.description: Final = description

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # openhab/things/chromecast:chromecast:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/status
        return cls(name=topic[15:-7], status=ThingStatusEnum(payload['status']),
                   detail=ThingStatusDetailEnum(payload['statusDetail']), description=payload.get('description', ''))

    def __repr__(self):
        description = f', description: "{self.description:s}"' if self.description else ''
        return f'<{self.__class__.__name__} name: {self.name:s}, ' \
               f'status: {self.status:s}, detail: {self.detail:s}{description:s}>'

    # def __init__(self, name: str = '', status: ThingStatusEnum = THING_STATUS_DEFAULT,
    #              detail: ThingStatusDetailEnum = THING_STATUS_DETAIL_DEFAULT, description: str = ''):


class ThingStatusInfoChangedEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar ThingStatusEnum status:
    :ivar ThingStatusDetailEnum detail:
    :ivar str description:
    :ivar ThingStatusEnum old_status:
    :ivar ThingStatusDetailEnum old_detail:
    :ivar str old_description:
    """
    name: str
    status: ThingStatusEnum
    detail: ThingStatusDetailEnum
    description: str
    old_status: ThingStatusEnum
    old_detail: ThingStatusDetailEnum
    old_description: str

    def __init__(self, name: str = '',
                 status: ThingStatusEnum = THING_STATUS_DEFAULT,
                 detail: ThingStatusDetailEnum = THING_STATUS_DETAIL_DEFAULT,
                 description: str = '',
                 old_status: ThingStatusEnum = THING_STATUS_DEFAULT,
                 old_detail: ThingStatusDetailEnum = THING_STATUS_DETAIL_DEFAULT,
                 old_description: str = ''):
        super().__init__()

        self.name: Final = name
        self.status: Final = status
        self.detail: Final = detail
        self.description: Final = description

        self.old_status: Final = old_status
        self.old_detail: Final = old_detail
        self.old_description: Final = old_description

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # openhab/things/chromecast:chromecast:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/statuschanged
        name = topic[15:-14]
        new, old = payload
        return cls(
            name=name,
            status=ThingStatusEnum(new['status']), detail=ThingStatusDetailEnum(new['statusDetail']),
            description=new.get('description', ''),
            old_status=ThingStatusEnum(old['status']), old_detail=ThingStatusDetailEnum(old['statusDetail']),
            old_description=old.get('description', '')
        )

    def __repr__(self):
        description = f', description: "{self.description:s}"' if self.description else ''
        old_description = f', old_description: "{self.old_description:s}"' if self.old_description else ''
        return f'<{self.__class__.__name__} name: {self.name}, ' \
               f'status: {self.status}, detail: {self.detail}{description:s}, ' \
               f'old_status: {self.old_status}, old_detail: {self.old_detail}{old_description:s}>'


class ThingConfigStatusInfoEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar Dict[str, str] config_messages:
    """
    name: str
    config_messages: Dict[str, str]

    def __init__(self, name: str = '', config_messages: Dict[str, str] = None):
        super().__init__()

        self.name: str = name
        self.config_messages: Dict[str, str] = config_messages if config_messages is not None else {}

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # openhab/things/zwave:device:gehirn:node29/config/status
        name = topic[15:-14]
        msgs = payload['configStatusMessages']
        return cls(
            name=name, config_messages={param_name: msg_type for d in msgs for param_name, msg_type in d.items()}
        )

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, config_messages: {self.config_messages}>'


class ThingFirmwareStatusInfoEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar str status:
    """
    name: str
    status: str

    def __init__(self, name: str = '', status: str = ''):
        super().__init__()
        self.name: str = name
        self.status: str = status

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # 'openhab/things/zwave:device:controller:my_node/firmware/status'
        return cls(name=topic[15:-16], status=payload['firmwareStatus'])

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name} status: {self.status}>'


class ThingRegistryBaseEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar str type:
    :ivar str label:
    :ivar str location:
    :ivar List[Dict[str, Any]] channels:
    :ivar Dict[str, Any] configuration:
    :ivar Dict[str, str] properties:
    """
    name: str
    type: str
    label: str
    location: str
    channels: List[Dict[str, Any]]
    configuration: Dict[str, Any]
    properties: Dict[str, str]

    def __init__(self, name: str, thing_type: str, label: str, location: str,
                 channels: List[Dict[str, Any]], configuration: Dict[str, Any],
                 properties: Dict[str, str]):
        super().__init__()

        # use name instead of uuid
        self.name: Final = name
        self.type: Final = thing_type

        # optional entries
        self.label: Final = label
        self.location: Final = location
        self.channels: Final = channels
        self.configuration: Final = configuration
        self.properties: Final = properties

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # 'openhab/things/astro:sun:0a94363608/added'
        return cls(
            name=payload['UID'], thing_type=payload['thingTypeUID'], label=payload['label'],
            location=payload.get('location', ''),
            channels=payload.get('channels', []),
            configuration=payload.get('configuration', {}),
            properties=payload.get('properties', {}),
        )

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}>'


class ThingAddedEvent(ThingRegistryBaseEvent):
    pass


class ThingRemovedEvent(ThingRegistryBaseEvent):
    pass


class ThingUpdatedEvent(ThingRegistryBaseEvent):
    @classmethod
    def from_dict(cls, topic: str, payload: List[Dict[str, Any]]):

        payload = payload[0]
        return cls(
            name=payload['UID'], thing_type=payload['thingTypeUID'], label=payload['label'],
            location=payload.get('location', ''),
            channels=payload.get('channels'),
            configuration=payload.get('configuration'),
            properties=payload.get('properties'),
        )
