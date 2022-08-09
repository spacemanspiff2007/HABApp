import random
import string
import sys
from pathlib import Path
from typing import Optional, Tuple

import pydantic
from pydantic import Field

from easyconfig.models import BaseModel

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal


QOS = Literal[0, 1, 2]


class TLSSettings(BaseModel):
    enabled: bool = Field(default=True, description='Enable TLS for the connection')
    ca_cert: Path = Field(
        default='', description='Path to a CA certificate that will be treated as trusted', alias='ca cert')
    insecure: bool = Field(
        default=False, description='Validate server hostname in server certificate')


class Connection(BaseModel):
    client_id: str = Field('HABApp-' + ''.join(random.choices(string.ascii_letters, k=13)),
                           description='ClientId that is used to uniquely identify this client on the mqtt broker.')
    host: str = Field('', description='Connect to this host. Empty string ("") disables the connection.')
    port: int = 1883
    user: str = ''
    password: str = ''
    tls: TLSSettings = Field(default_factory=TLSSettings)


class Subscribe(BaseModel):
    qos: QOS = Field(default=0, description='Default QoS for subscribing')
    topics: Tuple[Tuple[str, Optional[QOS]], ...] = Field(default=('#', ))

    @pydantic.validator('topics', pre=True)
    def parse_topics(cls, v):
        if not isinstance(v, (list, tuple, set)):
            raise ValueError('must be a list')
        ret = []
        for e in v:
            if isinstance(e, str):
                e = (e, None)
            ret.append(tuple(e))
        return tuple(ret)


class Publish(BaseModel):
    qos: QOS = Field(default=0, description='Default QoS when publishing values')
    retain: bool = Field(default=False, description='Default retain flag when publishing values')


class General(BaseModel):
    listen_only: bool = Field(False, description='If True HABApp does not publish any value to the broker')


class MqttConfig(BaseModel):
    """MQTT configuration"""

    connection: Connection = Field(default_factory=Connection)
    subscribe: Subscribe = Field(default_factory=Subscribe)
    publish: Publish = Field(default_factory=Publish)
    general: General = Field(default_factory=General)
