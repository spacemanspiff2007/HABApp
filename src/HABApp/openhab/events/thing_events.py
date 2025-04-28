from typing import Any, Final

from HABApp.openhab.definitions import ThingStatusDetailEnum, ThingStatusEnum
from HABApp.openhab.definitions.things import THING_STATUS_DEFAULT, THING_STATUS_DETAIL_DEFAULT

from .base_event import OpenhabEvent


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
                 detail: ThingStatusDetailEnum = THING_STATUS_DETAIL_DEFAULT, description: str = '') -> None:
        super().__init__()

        self.name: Final = name
        self.status: Final = status
        self.detail: Final = detail
        self.description: Final = description

    def __repr__(self) -> str:
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
                 old_description: str = '') -> None:
        super().__init__()

        self.name: Final = name
        self.status: Final = status
        self.detail: Final = detail
        self.description: Final = description

        self.old_status: Final = old_status
        self.old_detail: Final = old_detail
        self.old_description: Final = old_description

    def __repr__(self) -> str:
        description = f', description: "{self.description:s}"' if self.description else ''
        old_description = f', old_description: "{self.old_description:s}"' if self.old_description else ''
        return f'<{self.__class__.__name__} name: {self.name}, ' \
               f'status: {self.status}, detail: {self.detail}{description:s}, ' \
               f'old_status: {self.old_status}, old_detail: {self.old_detail}{old_description:s}>'


class ThingConfigStatusInfoEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar dict[str, str] config_messages:
    """
    name: str
    config_messages: dict[str, str]

    def __init__(self, name: str = '', config_messages: dict[str, str] = None) -> None:
        super().__init__()

        self.name: str = name
        self.config_messages: dict[str, str] = config_messages if config_messages is not None else {}

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} name: {self.name}, config_messages: {self.config_messages}>'


class ThingFirmwareStatusInfoEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar str status:
    """
    name: str
    status: str

    def __init__(self, name: str = '', status: str = '') -> None:
        super().__init__()
        self.name: str = name
        self.status: str = status

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} name: {self.name} status: {self.status}>'


class ThingRegistryBaseEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar str type:
    :ivar str label:
    :ivar str location:
    :ivar tuple[dict[str, Any], ...] channels:
    :ivar dict[str, Any] configuration:
    :ivar dict[str, str] properties:
    """
    name: str
    type: str
    label: str
    location: str
    channels: tuple[dict[str, Any], ...]
    configuration: dict[str, Any]
    properties: dict[str, str]

    def __init__(self, name: str, thing_type: str, label: str, location: str,
                 channels: tuple[dict[str, Any], ...], configuration: dict[str, Any],
                 properties: dict[str, str]) -> None:
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

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} name: {self.name}>'


class ThingAddedEvent(ThingRegistryBaseEvent):
    pass


class ThingRemovedEvent(ThingRegistryBaseEvent):
    pass


class ThingUpdatedEvent(ThingRegistryBaseEvent):
    pass
