from enum import Enum
from typing import ClassVar

from easyconfig.models import BaseModel
from pydantic import AnyHttpUrl, ByteSize, Field, TypeAdapter, field_validator

from HABApp.config.easyconfig_extention import EasyConfigField


class Ping(BaseModel):
    enabled: bool = Field(
        True,
        description='If enabled the configured item will show how long it takes to send '
        'an update from HABApp and get the updated value back from openHAB '
        'in milliseconds',
    )
    item: str = Field('HABApp_Ping', description='Name of the Numberitem')
    interval: int | float = Field(10, description='Seconds between two pings', ge=0.1)


class General(BaseModel):
    listen_only: bool = Field(False, description='If True HABApp does not change anything on the openHAB instance.')
    wait_for_openhab: bool = Field(
        True,
        description='If True HABApp will wait for a successful openHAB connection before loading any rules on startup',
    )

    # Advanced settings
    min_start_level: int = EasyConfigField(
        70,
        ge=0,
        le=100,
        in_file=False,
        description='Minimum openHAB start level to load items and listen to events',
    )

    # Minimum uptime
    min_uptime: int = EasyConfigField(
        60,
        ge=0,
        le=3600 * 2,
        in_file=False,
        description='Minimum openHAB uptime in seconds to load items and listen to events',
    )


class EventTypeFilterEnum(str, Enum):
    OFF = 'OFF'
    AUTO = 'AUTO'
    CONFIG = 'CONFIG'

    def is_auto(self) -> bool:
        return self == EventTypeFilterEnum.AUTO

    def is_config(self) -> bool:
        return self == EventTypeFilterEnum.CONFIG


class WebsocketEventFilter(BaseModel):
    event_type: EventTypeFilterEnum = Field(
        EventTypeFilterEnum.AUTO,
        alias='type',
        description='Configure the event type filter. "OFF" to allow all events, "AUTO" to allow the recommended '
        'events or "CONFIG" to use the event types from the "types allowed" field.',
    )
    types_allowed: tuple[str, ...] = Field(
        (), alias='types allowed', description='List of event types that will be allowed'
    )


class Websocket(BaseModel):
    max_msg_size: ByteSize = Field(
        ByteSize(4 * 1024 * 1024), # 4Mib
        alias='maximum message size',
        description='Maximum message size for a websocket message. '
        'Increase only if you get error messages or disconnects e.g. if you use large images.',
    )

    event_filter: WebsocketEventFilter = Field(
        default_factory=WebsocketEventFilter,
        alias='event filter',
        description='Configuration of server side event filters which will be applied to the websocket connection.',
    )

    ping_interval: int | float = Field(
        7, alias='ping interval', description='Interval for ping messages in seconds', gt=0
    )


    _VALID_BYTE_SIZES: ClassVar[dict[str, int]] = {
        '128kib': 128 * 1024,
        '256kib': 256 * 1024,
        '512kib': 512 * 1024,
        '1Mib': 1 * 1024 * 1024,
        '2Mib': 2 * 1024 * 1024,
        '4Mib': 4 * 1024 * 1024,
        '8Mib': 8 * 1024 * 1024,
        '16Mib': 16 * 1024 * 1024,
        '32Mib': 32 * 1024 * 1024,
        '64Mib': 64 * 1024 * 1024,
        '128Mib': 128 * 1024 * 1024,
    }

    @field_validator('max_msg_size')
    @classmethod
    def validate_see_buffer(cls, value: ByteSize) -> ByteSize:
        if not value in cls._VALID_BYTE_SIZES.values():
            msg = f'Value must be one of {", ".join(cls._VALID_BYTE_SIZES.keys())}'
            raise ValueError(msg)

        return value


class Connection(BaseModel):
    url: str = Field(
        'http://localhost:8080', description='Connect to this url. Empty string ("") disables the connection.'
    )
    user: str = ''
    password: str = ''
    verify_ssl: bool = Field(True, description='Check certificates when using https')

    websocket: Websocket = EasyConfigField(
        default_factory=Websocket,
        in_file=False,
        description='Options for the websocket connection which is used to connect to the openHAB event bus.',
    )

    @field_validator('url')
    @classmethod
    def validate_url(cls, value: str) -> str:
        if value:
            TypeAdapter(AnyHttpUrl).validate_python(value)
        return value


class OpenhabConfig(BaseModel):
    connection: Connection = Field(default_factory=Connection)
    general: General = Field(default_factory=General)
    ping: Ping = Field(default_factory=Ping)
