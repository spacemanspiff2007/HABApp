import logging
import typing
import ujson

import paho.mqtt.client as mqtt

import HABApp
from HABApp.util import log_exception

from HABApp.runtime.shutdown_helper import ShutdownHelper
from ..config import Mqtt as MqttConfig

from .events import MqttValueUpdateEvent, MqttValueChangeEvent

log = logging.getLogger('HABApp.mqtt.connection')
log_msg = logging.getLogger('HABApp.EventBus.mqtt')


class MqttConnection:
    def __init__(self, mqtt_config: MqttConfig, shutdown_helper: ShutdownHelper):
        assert isinstance(mqtt_config, MqttConfig)

        self.loop_started = False
        self.connected = False

        self.client: mqtt.Client = None

        self.subscriptions: typing.List[typing.Tuple[str, int]] = []

        # config changes
        self.__config = mqtt_config
        self.__config.subscribe.subscribe_for_changes(self.subscription_changed)
        self.__config.connection.subscribe_for_changes(self.connect)

        # shutdown
        shutdown_helper.register_func(self.disconnect)

        self.interface: HABApp.mqtt.MqttInterface = HABApp.mqtt.mqtt_interface.get_mqtt_interface(self, self.__config)

    def connect(self):
        if not self.__config.connection.host:
            log.info('MQTT disabled')
            self.disconnect()
            return None

        if self.connected:
            log.info('disconnecting')
            self.client.disconnect()
            self.connected = False

        self.client = mqtt.Client(
            client_id=self.__config.connection.client_id,
            clean_session=False
        )

        if self.__config.connection.tls:
            self.client.tls_set()

            # we can only set tls_insecure if we have a tls connection
            if self.__config.connection.tls_insecure:
                log.warning('Verification of server hostname in server certificate disabled!')
                log.warning('Use this only for testing, not for a real system!')
                self.client.tls_insecure_set(True)

        # set user if required
        user = self.__config.connection.user
        pw = self.__config.connection.password
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
            self.__config.connection.host,
            port=self.__config.connection.port,
            keepalive=60
        )

        log.info(f'Connecting to {self.__config.connection.host}:{self.__config.connection.port}')

        if not self.loop_started:
            self.client.loop_start()
        self.loop_started = True

    @log_exception
    def subscription_changed(self):
        if not self.connected:
            return None

        if self.subscriptions:
            unsubscribe = [k[0] for k in self.subscriptions]
            log.debug(f'Unsubscribing from:')
            for t in unsubscribe:
                log.debug(f' - "{t}"')
            self.client.unsubscribe(unsubscribe)

        topics = self.__config.subscribe.topics
        default_qos = self.__config.subscribe.qos
        self.subscriptions = [(topic, qos if qos is not None else default_qos) for topic, qos in topics]
        log.debug(f'Subscribing to:')
        for topic, qos in self.subscriptions:
            log.debug(f' - "{topic}" (QoS {qos:d})')
        self.client.subscribe(self.subscriptions)

    @log_exception
    def on_connect(self, client, userdata, flags, rc):
        log.log(logging.INFO if not rc else logging.ERROR, mqtt.connack_string(rc))
        if rc:
            return None
        self.connected = True

        self.subscriptions.clear()
        self.subscription_changed()

    @log_exception
    def on_disconnect(self, client, userdata, rc):
        log.log(logging.INFO if not rc else logging.ERROR, f'Disconnect: {mqtt.error_string(rc)} ({rc})')
        self.connected = False

    @log_exception
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

        # get the mqtt item
        _item = HABApp.mqtt.items.MqttItem.get_create_item(topic)

        # remeber state and update item before doing callbacks
        _old_state = _item.value
        _item.set_value(payload)

        # Post events
        HABApp.core.EventBus.post_event(topic, MqttValueUpdateEvent(topic, payload))
        if _old_state != payload:
            HABApp.core.EventBus.post_event(topic, MqttValueChangeEvent(topic, payload, _old_state))

    def disconnect(self):
        if self.connected:
            self.client.disconnect()
            self.connected = False
        if self.loop_started:
            self.client.loop_stop()
            self.loop_started = False

        self.client = None
