from enum import Enum

from easyconfig.models import BaseModel, Field
from pydantic import AnyHttpUrl, ByteSize, TypeAdapter, field_validator


class Ping(BaseModel):
    enabled: bool = Field(True, description='If enabled the configured item will show how long it takes to send '
                                            'an update from HABApp and get the updated value back from openHAB '
                                            'in milliseconds')
    item: str = Field('HABApp_Ping', description='Name of the Numberitem')
    interval: int | float = Field(10, description='Seconds between two pings', ge=0.1)


class General(BaseModel):
    listen_only: bool = Field(
        False, description='If True HABApp does not change anything on the openHAB instance.'
    )
    wait_for_openhab: bool = Field(
        True,
        description='If True HABApp will wait for a successful openHAB connection before loading any rules on startup'
    )

    # Advanced settings
    min_start_level: int = Field(
        70, ge=0, le=100, in_file=False,
        description='Minimum openHAB start level to load items and listen to events',
    )

    # Minimum uptime
    min_uptime: int = Field(
        60, ge=0, le=3600 * 2, in_file=False,
        description='Minimum openHAB uptime in seconds to load items and listen to events',
    )


class EventTypeFilterEnum(str, Enum):
    OFF = 'OFF'
    AUTO = 'AUTO'
    CONFIG = 'CONFIG'

    def is_auto(self):
        return self == EventTypeFilterEnum.AUTO

    def is_config(self):
        return self == EventTypeFilterEnum.CONFIG


class WebsocketEventFilter(BaseModel):
    event_type: EventTypeFilterEnum = Field(
        EventTypeFilterEnum.AUTO, alias='type',
        description='Configure the event type filter. "OFF" to allow all events, "AUTO" to allow the recommended '
                    'events or "CONFIG" to use the event types from the "types allowed" field.'
    )
    types_allowed: tuple[str, ...] = Field(
        (), alias='types allowed', description='List of event types that will be allowed'
    )


class Websocket(BaseModel):
    max_msg_size: ByteSize = Field(
        '4Mib', alias='maximum message size',
        description='Maximum message size for a websocket message. '
        'Increase only if you get error messages or disconnects e.g. if you use large images.'
    )

    event_filter: WebsocketEventFilter = Field(
        default_factory=WebsocketEventFilter, alias='event filter',
        description='Configuration of server side event filters which will be applied to the websocket connection.'
    )

    ping_interval: int | float = Field(
        7, alias='ping interval', description='Interval for ping messages in seconds', gt=0
    )

    @field_validator('max_msg_size')
    def validate_see_buffer(cls, value: ByteSize):
        valid_values = (
            '128kib', '256kib', '512kib',
            '1Mib', '2Mib', '4Mib', '8Mib', '16Mib', '32Mib', '64Mib', '128Mib'
        )

        for _v in valid_values:
            # noinspection PyProtectedMember
            if value == ByteSize._validate(_v, None):
                return value

        msg = f'Value must be one of {", ".join(valid_values)}'
        raise ValueError(msg)


class Connection(BaseModel):
    url: str = Field(
        'http://localhost:8080', description='Connect to this url. Empty string ("") disables the connection.')
    user: str = ''
    password: str = ''
    verify_ssl: bool = Field(True, description='Check certificates when using https')

    websocket: Websocket = Field(
        default_factory=Websocket, in_file=False, description='Options for the websocket connection which is used'
        'to connect to the openHAB event bus.'
    )

    @field_validator('url')
    def validate_url(cls, value: str):
        if value:
            TypeAdapter(AnyHttpUrl).validate_python(value)
        return value


class OpenhabConfig(BaseModel):
    connection: Connection = Field(default_factory=Connection)
    general: General = Field(default_factory=General)
    ping: Ping = Field(default_factory=Ping)
