from typing import Union

from easyconfig.models import BaseModel
from pydantic import Field, AnyHttpUrl, constr, ByteSize, validator


class Ping(BaseModel):
    enabled: bool = Field(True, description='If enabled the configured item will show how long it takes to send '
                                            'an update from HABApp and get the updated value back from openHAB '
                                            'in milliseconds')
    item: str = Field('HABApp_Ping', description='Name of the Numberitem')
    interval: int = Field(10, description='Seconds between two pings')


class General(BaseModel):
    listen_only: bool = Field(
        False, description='If True HABApp will not change anything on the openHAB instance.'
    )
    wait_for_openhab: bool = Field(
        True,
        description='If True HABApp will wait for items from the openHAB instance before loading any rules on startup'
    )


class Connection(BaseModel):
    url: Union[AnyHttpUrl, constr(max_length=0, strict=True)] = \
        Field('http://localhost:8080', description='Connect to this url')
    user: str = ''
    password: str = ''
    verify_ssl: bool = Field(True, description='Check certificates when using https')

    buffer: ByteSize = Field(
        '128kib', in_file=False, description=
        'Buffer for reading lines in the SSE event handler. This is the buffer'
        'that gets allocated for every(!) request and SSE message that the client processes. '
        'Increase only if you get error messages or disconnects e.g. if you use large images.'
    )

    @validator('buffer', always=True)
    def validate_see_buffer(cls, value: ByteSize):
        valid_values = (
            '128kib', '256kib', '512kib', '1Mib', '2Mib', '4Mib', '8Mib', '16Mib', '32Mib', '64Mib', '128Mib')

        for _v in valid_values:
            if value == ByteSize.validate(_v):
                return value

        raise ValueError(f'Value must be one of {", ".join(valid_values)}')


class OpenhabConfig(BaseModel):
    ping: Ping = Ping()
    connection: Connection = Connection()
    general: General = General()
