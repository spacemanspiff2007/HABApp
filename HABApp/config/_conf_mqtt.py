import typing

from EasyCo import ConfigContainer, ConfigEntry
from voluptuous import Invalid


def MqttTopicValidator(v, msg=''):
    if isinstance(v, str):
        return [(v, 0)]

    ret = []
    for i, val in enumerate(v):
        qos = 0
        if i < len(v) - 1:
            qos = v[i + 1]

        if not isinstance(val, str) and not isinstance(val, int):
            raise Invalid(msg or "Topics must consist of int and string!")

        if not isinstance(val, str):
            continue

        if isinstance(qos, int):
            if qos not in [0, 1, 2]:
                raise Invalid(msg or ("QoS must be 0, 1 or 2"))
        else:
            qos = None

        ret.append((val, qos))
    return ret


class Connection(ConfigContainer):
    client_id: str = 'HABApp'
    host: str = ''
    port: int = 8883
    user: str = ''
    password: str = ''
    tls: bool = True
    tls_insecure: bool = False


class Subscribe(ConfigContainer):
    qos: int = ConfigEntry(default=0, description='Default QoS for subscribing')
    topics: typing.List[typing.Union[str, int]] = ConfigEntry(
        default_factory=lambda: list(('#', 0)), validator=MqttTopicValidator
    )


class Publish(ConfigContainer):
    qos: int = ConfigEntry(default=0, description='Default QoS when publishing values')
    retain: bool = ConfigEntry(default=False, description='Default retain flag when publishing values')


class General(ConfigContainer):
    listen_only: bool = ConfigEntry(
        False, description='If True HABApp will not publish any value to the broker'
    )


class Mqtt(ConfigContainer):
    connection = Connection()
    subscribe = Subscribe()
    publish = Publish()
    general = General()
