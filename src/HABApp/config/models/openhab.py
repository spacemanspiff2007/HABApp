from typing import Union

from easyconfig import ConfigModel
from pydantic import Field, AnyHttpUrl, constr


class Ping(ConfigModel):
    enabled: bool = Field(True, description='If enabled the configured item will show how long it takes to send '
                                            'an update from HABApp and get the updated value back from openHAB'
                                            'in milliseconds')
    item: str = Field('HABApp_Ping', description='Name of the Numberitem')
    interval: int = Field(10, description='Seconds between two pings')


class General(ConfigModel):
    listen_only: bool = Field(
        False, description='If True HABApp will not change anything on the openHAB instance.'
    )
    wait_for_openhab: bool = Field(
        True,
        description='If True HABApp will wait for items from the openHAB instance before loading any rules on startup'
    )


class Connection(ConfigModel):
    url: Union[AnyHttpUrl, constr(max_length=0, strict=True)] = \
        Field('http://localhost:8080', description='Connect to this url')
    user: str = ''
    password: str = ''
    verify_ssl: bool = Field(True, description='Check certificates when using https')


class OpenhabConfig(ConfigModel):
    ping: Ping = Ping()
    connection: Connection = Connection()
    general: General = General()
