import re

from voluptuous import Invalid

from .configentry import ConfigEntry, ConfigEntryContainer


def TimeZoneValidator(msg=None):
    __re = re.compile(r'[+-]\d{4}')
    
    def f(v):
        v = str(v)
        if __re.fullmatch(v):
            return v
        else:
            raise Invalid(msg or (f"incorrect timezone ({v})! Example: +1000 or -1030"))
    
    return f


class Ping(ConfigEntry):
    def __init__(self):
        super().__init__()
        self.enabled = False
        self.item = ''
        self.interval = 10


class General(ConfigEntry):
    def __init__(self):
        super().__init__()
        self.timezone = '+1000'
        self._entry_validators['timezone'] = TimeZoneValidator()


class Connection(ConfigEntry):
    def __init__(self):
        super().__init__()
        self.host = 'localhost'
        self.port = 8080
        self.user = ''
        self.password = ''
        
        self._entry_kwargs['user'] = {'default': ''}
        self._entry_kwargs['password'] = {'default': ''}


class Openhab(ConfigEntryContainer):
    def __init__(self):
        self.ping = Ping()
        self.connection = Connection()
        self.general = General()
