import paho.mqtt.client as mqtt

import HABApp


class MqttConnection:
    def __init__(self, parent):
        assert isinstance(parent, HABApp.Runtime)
        self.runtime: HABApp.Runtime = parent

        self.client : mqtt.Client = None

    def connect(self):
        self.client = mqtt.Client()

        # todo
        if self.runtime.config.mqtt:
            self.client.tls_set()

        # set user if required
        user = self.runtime.config.mqtt.connection.user
        pw = self.runtime.config.mqtt.connection.password
        if user:
            self.client.username_pw_set(
                user,
                pw if pw else None
            )

        self.client.connect(
            self.runtime.config.mqtt.connection.host,
            port=self.runtime.config.mqtt.connection.port,
            keepalive=60
        )

        self.client.loop_start()