import logging

import HABApp
from HABApp.mqtt.mqtt_connection import connect, STATUS
from pathlib import Path


def test_connect(caplog):
    HABApp.CONFIG.mqtt.connection.host = 'localhost'
    HABApp.CONFIG.mqtt.connection.tls.ca_cert = Path('invalid_file_path')

    connect()

    assert STATUS.client is None
    assert STATUS.connected is False
    assert STATUS.loop_started is False

    msg = ('HABApp.mqtt.connection', logging.ERROR, 'Ca cert file does not exist: invalid_file_path')
    assert msg in caplog.record_tuples
