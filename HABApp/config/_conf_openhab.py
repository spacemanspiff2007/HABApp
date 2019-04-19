from .configentry import ConfigEntry, ConfigEntryContainer


class Ping(ConfigEntry):
    def __init__(self):
        super().__init__()
        self.enabled = False
        self.item = ''
        self.interval = 10


class General(ConfigEntry):
    def __init__(self):
        super().__init__()
        self.listen_only = False


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
