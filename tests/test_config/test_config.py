import logging
import re

from easyconfig.yaml import yaml_safe
from tests.helpers import LogCollector

from HABApp import CONFIG
from HABApp.config.models.mqtt import Subscribe


def test_default_file() -> None:
    msg = re.sub(r'identifier:\s+HABApp-\w{13}', f'identifier: HABApp-{"TestFile":13s}', CONFIG.generate_default_yaml())
    assert '\n' + msg == '''
directories:
  logging: log    # Folder where the logs will be written to
  rules: rules    # Folder from which the rule files will be loaded
  param: params   # Folder from which the parameter files will be loaded
  config: config  # Folder from which configuration files (e.g. for textual thing configuration) will be loaded
  lib: lib        # Folder where additional libraries can be placed
location:
  latitude: 0.0
  longitude: 0.0
  elevation: 0.0
  country: ''      # ISO 3166-1 Alpha-2 country code
  subdivision: ''  # The subdivision (e.g. state or province) as a ISO 3166-2 code or its alias
mqtt:
  connection:
    identifier: HABApp-TestFile        # Identifier that is used to uniquely identify this client on the mqtt broker.
    host: ''                           # Connect to this host. Empty string ("") disables the connection.
    port: 1883
    user: ''
    password: ''
    tls:
      enabled: true    # Enable TLS for the connection
      ca cert: .       # Path to a CA certificate that will be treated as trusted
      insecure: false  # Validate server hostname in server certificate
  subscribe:
    qos: 0   # Default QoS for subscribing
    topics:
    - '#'
    - topic/with/default/qos
    - - topic/with/qos
      - 1
  publish:
    qos: 0         # Default QoS when publishing values
    retain: false  # Default retain flag when publishing values
  general:
    listen_only: false   # If True HABApp does not publish any value to the broker
openhab:
  connection:
    url: http://localhost:8080   # Connect to this url. Empty string ("") disables the connection.
    user: ''
    password: ''
    verify_ssl: true             # Check certificates when using https
  general:
    listen_only: false      # If True HABApp does not change anything on the openHAB instance.
    wait_for_openhab: true  # If True HABApp will wait for a successful openHAB connection before loading any rules on startup
  ping:
    enabled: true      # If enabled the configured item will show how long it takes to send an update from HABApp and get the updated value back from openHAB in milliseconds
    item: HABApp_Ping  # Name of the Numberitem
    interval: 10       # Seconds between two pings
'''


def test_migrate(test_logs: LogCollector) -> None:
    text = '''
  subscribe:
    qos: 0   # Default QoS for subscribing
    topics:
    - - '#'
      - 
  publish:
    '''

    obj = yaml_safe.load(text)
    Subscribe.model_validate(obj['subscribe'])

    test_logs.add_expected(
        'HABApp.Config', logging.WARNING,
        [
            'Empty QoS is not longer allowed for subscribing to topics.',
            'Specify QOS or remove empty entry, e.g from',
            '  - - #',
            '    - ',
            'to',
            '  - #',
        ]
    )
