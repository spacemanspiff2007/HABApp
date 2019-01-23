import logging
import ujson

import paho.mqtt.client as mqtt

import HABApp
from HABApp.util import PrintException

log = logging.getLogger('HABApp.mqtt.connection')
log_msg = logging.getLogger('HABApp.Events.mqtt')


class MqttConnection:
    def __init__(self, parent):
        assert isinstance(parent, HABApp.Runtime)
        self.runtime: HABApp.Runtime = parent

        self.loop_started = False
        self.connected = False

        self.client: mqtt.Client = None

        self.subscriptions = []
        self.value_cache = {}

        # config changes
        self.runtime.config.mqtt.subscribe.subscribe_for_changes(self.subscription_changed)
        self.runtime.config.mqtt.connection.subscribe_for_changes(self.connect)

        # shutdown
        self.runtime.shutdown.register_func(self.disconnect)

    def connect(self):
        if not self.runtime.config.mqtt.connection.host:
            log.info('MQTT disabled')
            self.disconnect()
            return None

        if self.connected:
            log.info('disconnecting')
            self.client.disconnect()
            self.connected = False

        self.client = mqtt.Client(
            client_id=self.runtime.config.mqtt.connection.client_id,
            clean_session=False
        )

        if self.runtime.config.mqtt.connection.tls:
            self.client.tls_set()

        if self.runtime.config.mqtt.connection.tls_insecure:
            log.warning('Verification of server hostname in server certificate disabled!')
            log.warning('Use this only for testing, not for a real system!')
            self.client.tls_insecure_set(True)

        # set user if required
        user = self.runtime.config.mqtt.connection.user
        pw = self.runtime.config.mqtt.connection.password
        if user:
            self.client.username_pw_set(
                user,
                pw if pw else None
            )

        # setup callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.process_msg

        self.client.connect_async(
            self.runtime.config.mqtt.connection.host,
            port=self.runtime.config.mqtt.connection.port,
            keepalive=60
        )

        if not self.loop_started:
            self.client.loop_start()
        self.loop_started = True

    @PrintException
    def subscription_changed(self):
        if not self.connected:
            return None

        if self.subscriptions:
            unsubscribe = [k[0] for k in self.subscriptions]
            for t in unsubscribe:
                log.debug(f'Unsubscribing from "{t}"')
            self.client.unsubscribe(unsubscribe)

        topics = self.runtime.config.mqtt.subscribe.topics
        default_qos = self.runtime.config.mqtt.subscribe.qos
        self.subscriptions = [(topic, qos if qos is not None else default_qos) for topic, qos in topics]
        for topic, qos in self.subscriptions:
            log.debug(f'Subscribing to "{topic}" (QoS {qos:d})')
        self.client.subscribe(self.subscriptions)

    @PrintException
    def on_connect(self, client, userdata, flags, rc):
        log.log(logging.INFO if not rc else logging.ERROR, mqtt.connack_string(rc))
        if rc:
            return None
        self.connected = True

        self.value_cache.clear()
        self.subscriptions.clear()
        self.subscription_changed()

    @PrintException
    def on_disconnect(self, client, userdata, rc):
        log.log(logging.INFO if not rc else logging.ERROR, "Unexpected disconnection")
        self.connected = False

    @PrintException
    def process_msg(self, client, userdata, message: mqtt.MQTTMessage):
        topic = message.topic
        payload = message.payload.decode("utf-8")

        if log_msg.isEnabledFor(logging.DEBUG):
            log_msg._log(logging.DEBUG, f'{topic} ({message.qos}): {payload}', [])

        # load json dict and list
        if payload.startswith('{') and payload.endswith('}') or payload.startswith('[') and payload.endswith(']'):
            try:
                payload = ujson.loads(payload)
            except ValueError:
                pass
        else:
            # try to cast to int/float
            try:
                payload = int(payload)
            except ValueError:
                try:
                    payload = float(payload)
                except ValueError:
                    pass

        __was = self.value_cache.get(topic, None)
        self.value_cache[topic] = payload

        HABApp.core.Events.post_event(topic, HABApp.core.ValueUpdateEvent(topic, payload))
        if __was is not None and __was != payload:
            HABApp.core.Events.post_event(topic, HABApp.core.ValueChangeEvent(topic, payload, __was))

    def publish(self, topic, payload, qos, retain):

        if qos is None:
            qos = self.runtime.config.mqtt.publish.qos
        if retain is None:
            retain = self.runtime.config.mqtt.publish.retain

        info = self.client.publish(topic, payload, qos, retain)
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            log.error(f'Could not publish to "{topic}": {mqtt.error_string(info.rc)}')

    def disconnect(self, rc):
        if self.connected:
            self.client.disconnect()
            self.connected = False
        if self.loop_started:
            self.client.loop_stop()
            self.loop_started = False
