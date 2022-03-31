import sys
from typing import Tuple, Optional

import pydantic
from easyconfig import BaseModel
from pydantic import Field

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal


QOS = Literal[0, 1, 2]


class Connection(BaseModel):
    client_id: str = 'HABApp'
    host: str = ''
    port: int = 8883
    user: str = ''
    password: str = ''
    tls: bool = True
    tls_ca_cert: str = Field(default='', description='Path to a CA certificate that will be treated as trusted')
    tls_insecure: bool = False


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
    listen_only: bool = Field(False, description='If True HABApp will not publish any value to the broker')


class MqttConfig(BaseModel):
    connection: Connection = Connection()
    subscribe: Subscribe = Subscribe()
    publish: Publish = Publish()
    general: General = General()
