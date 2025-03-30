import logging
import random
import string
from collections.abc import Generator
from pathlib import Path
from typing import Literal

import pydantic
from easyconfig.models import BaseModel
from pydantic import Field


QOS = Literal[0, 1, 2]


class TLSSettings(BaseModel):
    enabled: bool = Field(default=True, description='Enable TLS for the connection')
    ca_cert: Path = Field(
        default=Path(''), description='Path to a CA certificate that will be treated as trusted', alias='ca cert')
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

    # implemented 2024.02.0
    @pydantic.model_validator(mode='before')
    @classmethod
    def _migrate_client_id(cls, data: dict) -> dict:
        if isinstance(data, dict) and 'client_id' in data:
            log = logging.getLogger('HABApp.Config')
            log.warning('"client_id" in mqtt.connection has been renamed to "identifier"')
            if 'identifier' not in data:
                data['identifier'] = data.pop('client_id')
        return data


class Subscribe(BaseModel):
    qos: QOS = Field(default=0, description='Default QoS for subscribing')
    topics: tuple[str | tuple[str, QOS], ...] = Field(default=('#', 'topic/with/default/qos', ('topic/with/qos', 1)))

    def get_topic_qos(self) -> Generator[tuple[str, QOS], None, None]:
        for obj in self.topics:
            if isinstance(obj, str):
                yield obj, self.qos
            else:
                yield obj

    # Implemented 2024.11.0
    @pydantic.model_validator(mode='before')
    @classmethod
    def _migrate_topics(cls, data: dict) -> dict:
        if isinstance(data, dict) and (topics := data.get('topics', [])) is not None:
            for i, topic_obj in enumerate(topics):
                if not isinstance(topic_obj, list):
                    continue
                topic, qos = topic_obj
                if qos is not None:
                    continue

                log = logging.getLogger('HABApp.Config')
                log.warning('Empty QoS is not longer allowed for subscribing to topics.')
                log.warning('Specify QOS or remove empty entry, e.g from')
                log.warning(f'  - - {topic:s}')
                log.warning('    - ')
                log.warning('to')
                log.warning(f'  - {topic:s}')

                topics[i] = topic

        return data


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
