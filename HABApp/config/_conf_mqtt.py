from voluptuous import All, Invalid, Length

from .configentry import ConfigEntry, ConfigEntryContainer


def MqttTopicValidator(msg=None):
    def f(v):
        if isinstance(v, str):
            return [(v, 0)]

        ret = []
        for i, val in enumerate(v):
            qos = 0
            if i < len(v) - 1:
                qos = v[i + 1]

            if not isinstance(val, str) and not isinstance(val, int):
                raise Invalid(msg or (f"Topics must consist of int and string!"))

            if not isinstance(val, str):
                continue

            if isinstance(qos, int):
                if qos not in [0, 1, 2]:
                    raise Invalid(msg or (f"QoS must be 0, 1 or 2"))
            else:
                qos = None

            ret.append((val, qos))
        return ret

    return f


class MqttConnection(ConfigEntry):
    def __init__(self):
        super().__init__()
        self._entry_name = 'connection'
        self.client_id = 'HABApp'
        self.host = ''
        self.port = 8883
        self.user = ''
        self.password = ''
        self.tls = True
        self.tls_insecure = False

        self._entry_validators['client_id'] = All(str, Length(min=1))

        self._entry_kwargs['password'] = {'default': ''}
        self._entry_kwargs['tls_insecure'] = {'default': False}


class Subscribe(ConfigEntry):
    def __init__(self):
        super().__init__()
        self.qos = 0
        self.topics = ['#', 0]

        self._entry_validators['topics'] = MqttTopicValidator()
        self._entry_kwargs['topics'] = {'default': [('#', 0)]}
        self._entry_kwargs['default_qos'] = {'default': 0}


class Publish(ConfigEntry):
    def __init__(self):
        super().__init__()
        self.qos = 0
        self.retain = False


class mqtt(ConfigEntry):
    def __init__(self):
        super().__init__()
        self.client_id = ''
        self.tls = True
        self.tls_insecure = False

        self._entry_kwargs['tls_insecure'] = {'default': False}


class Mqtt(ConfigEntryContainer):
    def __init__(self):
        self.connection = MqttConnection()
        self.subscribe = Subscribe()
        self.publish = Publish()
