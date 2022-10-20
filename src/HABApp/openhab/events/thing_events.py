from typing import Optional, List, Dict, Any

from .base_event import OpenhabEvent


class ThingStatusInfoEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar str status:
    :ivar str detail:
    """
    name: str
    status: str
    detail: str

    def __init__(self, name: str = '', status: str = '', detail: str = ''):
        super().__init__()

        self.name: str = name
        self.status: str = status
        self.detail: str = detail

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # openhab/things/chromecast:chromecast:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/status
        return cls(name=topic[15:-7], status=payload['status'], detail=payload['statusDetail'])

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, status: {self.status}, detail: {self.detail}>'


class ThingStatusInfoChangedEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar str status:
    :ivar str detail:
    :ivar str old_status:
    :ivar str old_detail:
    """
    name: str
    status: str
    detail: str
    old_status: str
    old_detail: str

    def __init__(self, name: str = '', status: str = '', detail: str = '', old_status: str = '', old_detail: str = ''):
        super().__init__()

        self.name: str = name
        self.status: str = status
        self.detail: str = detail
        self.old_status: str = old_status
        self.old_detail: str = old_detail

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # openhab/things/chromecast:chromecast:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/statuschanged
        name = topic[15:-14]
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
    """
    :ivar str name:
    :ivar Dict[str, str] config_messages:
    """
    name: str
    config_messages: Dict[str, str]

    def __init__(self, name: str = '', config_messages: Optional[Dict[str, str]] = None):
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
    :ivar List[Dict[str, Any]] channels:
    :ivar Dict[str, Any] configuration:
    :ivar Dict[str, str] properties:
    """
    name: str
    type: str
    label: str
    channels: List[Dict[str, Any]]
    configuration: Dict[str, Any]
    properties: Dict[str, str]

    def __init__(self, name: str = '', thing_type: str = '', label: str = '',
                 channels: Optional[List[Dict[str, Any]]] = None, configuration: Optional[Dict[str, Any]] = None,
                 properties: Optional[Dict[str, str]] = None):
        super().__init__()

        # use name instead of uuid
        self.name: str = name
        self.type: str = thing_type

        # optional entries
        self.label: str = label
        self.channels: List[Dict[str, Any]] = channels if channels is not None else []
        self.configuration: Dict[str, Any] = configuration if configuration is not None else {}
        self.properties: Dict[str, str] = properties if properties is not None else {}

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # 'openhab/things/astro:sun:0a94363608/added'
        return cls(
            name=payload['UID'], thing_type=payload['thingTypeUID'], label=payload['label'],
            channels=payload.get('channels'), configuration=payload.get('configuration'),
            properties=payload.get('properties'),
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
            channels=payload.get('channels'), configuration=payload.get('configuration'),
            properties=payload.get('properties'),
        )
