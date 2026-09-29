import random
import string
from collections.abc import Generator
from pathlib import Path
from typing import Literal, TypeAlias

from easyconfig.models import BaseModel
from pydantic import Field


QOS: TypeAlias = Literal[0, 1, 2]


class TLSSettings(BaseModel):
    enabled: bool = Field(default=True, description='Enable TLS for the connection')
    ca_cert: Path = Field(
        default='', description='Path to a CA certificate that will be treated as trusted', alias='ca cert')
    insecure: bool = Field(
        default=False, description='Validate server hostname in server certificate')


class Connection(BaseModel):
    identifier: str = Field('HABApp-' + ''.join(random.choices(string.ascii_letters, k=13)),
                            description='Identifier that is used to uniquely identify this client on the mqtt broker.')
    host: str = Field('', description='Connect to this host. Empty string ("") disables the connection.')
    port: int = 1883
    user: str = ''
    password: str = ''
    tls: TLSSettings = Field(default_factory=TLSSettings)


class Subscribe(BaseModel):
    qos: QOS = Field(default=0, description='Default QoS for subscribing')
    topics: tuple[str | tuple[str, QOS], ...] = Field(default=('#', 'topic/with/default/qos', ('topic/with/qos', 1)))

    def get_topic_qos(self) -> Generator[tuple[str, QOS], None, None]:
        for obj in self.topics:
            if isinstance(obj, str):
                yield obj, self.qos
            else:
                yield obj


class Publish(BaseModel):
    qos: QOS = Field(default=0, description='Default QoS when publishing values')
    retain: bool = Field(default=False, description='Default retain flag when publishing values')


class General(BaseModel):
    listen_only: bool = Field(False, description='If True HABApp does not publish any value to the broker')


class MqttConfig(BaseModel):
    """Configuration for MQTT. Changes in these sections are typically applied without a restart"""

    connection: Connection = Field(default_factory=Connection)
    subscribe: Subscribe = Field(default_factory=Subscribe)
    publish: Publish = Field(default_factory=Publish)
    general: General = Field(default_factory=General)
