from base64 import b64encode
from enum import StrEnum
from typing import Final, Literal

import aiohttp
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


class EventTypeFilterEnum(StrEnum):
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


_OH_TOKEN_PREFIX: Final = 'oh.'


class Connection(BaseModel):
    url: str = Field(
        'http://localhost:8080', description='Connect to this url. Empty string ("") disables the connection.')
    user: str = Field('', description='Username or openHAB access token (starts with "oh.")')
    password: str = Field('', description='Password for basic authentication or empty when using access token')
    verify_ssl: bool = Field(True, description='Check certificates when using https')

    websocket: Websocket = Field(
        default_factory=Websocket, in_file=False, description='Options for the websocket connection which is used'
        'to connect to the openHAB event bus.'
    )

    @field_validator('url')
    @classmethod
    def validate_url(cls, value: str) -> str:
        if value:
            TypeAdapter(AnyHttpUrl).validate_python(value)
        return value

    @field_validator('password')
    @classmethod
    def _validate_password(cls, value: str) -> str:
        if value.startswith(_OH_TOKEN_PREFIX):
            msg: Final = (f'OpenHAB access token detected in "password" field ({_OH_TOKEN_PREFIX:s} prefix), '
                          f'please move it to the "user" field in the configuration file.')
            raise ValueError(msg)
        return value

    def auth_complete(self) -> bool:
        return bool(self.is_token() or (self.user and self.password))

    def is_token(self) -> bool:
        return self.user.startswith(_OH_TOKEN_PREFIX)

    def build_url_token(self) -> str:
        # we use token as auth
        if self.is_token():
            return self.user

        # basic auth
        return b64encode(f'{self.user}:{self.password}'.encode()).decode()

    def build_basic_auth_header(self) -> tuple[tuple[Literal['Authorization'], str]]:
        return (('Authorization', aiohttp.encode_basic_auth(self.user, self.password)), )


class OpenhabConfig(BaseModel):
    """Configuration for openHAB. Changes in these sections are typically applied without a restart"""
    connection: Connection = Field(default_factory=Connection)
    general: General = Field(default_factory=General)
    ping: Ping = Field(default_factory=Ping)
