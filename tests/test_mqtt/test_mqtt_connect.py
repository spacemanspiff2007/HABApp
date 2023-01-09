import logging

import HABApp
from HABApp.mqtt.mqtt_connection import connect, STATUS
from pathlib import Path

from tests.helpers import LogCollector


def test_connect(test_logs: LogCollector):
    HABApp.CONFIG.mqtt.connection.host = 'localhost'
    HABApp.CONFIG.mqtt.connection.tls.ca_cert = Path('invalid_file_path')

    connect()

    assert STATUS.client is None
    assert STATUS.connected is False
    assert STATUS.loop_started is False

    test_logs.add_expected('HABApp.mqtt.connection', logging.ERROR, 'Ca cert file does not exist: invalid_file_path')
