from EasyCo import ConfigContainer, ConfigEntry


class Ping(ConfigContainer):
    enabled: bool = ConfigEntry(True, description='If enabled the configured item will show how long it takes to send '
                                                  'an update from HABApp and get the updated value back from openhab'
                                                  'in milliseconds')
    item: str = ConfigEntry('HABApp_Ping', description='Name of the item')
    interval: int = ConfigEntry(10, description='Seconds between two pings')


class General(ConfigContainer):
    listen_only: bool = ConfigEntry(
        False, description='If True HABApp will not change anything on the openHAB instance.'
    )
    wait_for_openhab: bool = ConfigEntry(
        False,
        description='If True HABApp will wait for items from the openHAB instance before loading any rules on startup'
    )


class Connection(ConfigContainer):
    host: str = 'localhost'
    port: int = 8080
    user: str = ''
    password: str = ''


class Openhab(ConfigContainer):
    ping = Ping()
    connection = Connection()
    general = General()
