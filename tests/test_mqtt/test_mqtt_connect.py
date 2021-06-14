import logging

import HABApp
from HABApp.mqtt.mqtt_connection import connect, STATUS


def test_connect(monkeypatch, caplog):
    HABApp.CONFIG.mqtt.connection.host = 'localhost'
    HABApp.CONFIG.mqtt.connection.tls_ca_cert = 'invalid_file_path'

    connect()

    assert STATUS.client is None
    assert STATUS.connected is False
    assert STATUS.loop_started is False

    msg = ('HABApp.mqtt.connection', logging.ERROR, 'Ca cert file does not exist: invalid_file_path')
    assert msg in caplog.record_tuples
