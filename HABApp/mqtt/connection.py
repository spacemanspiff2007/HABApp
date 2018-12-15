import logging
import paho.mqtt.client as mqtt


import HABApp
from HABApp.util import PrintException
from .events import MqttChange, MqttUpdate

log = logging.getLogger('HABApp.mqtt.connection')
log_msg = logging.getLogger('HABApp.mqtt.message')

class MqttConnection:
    def __init__(self, parent):
        assert isinstance(parent, HABApp.Runtime)
        self.runtime: HABApp.Runtime = parent

        self.client : mqtt.Client = None

        self.subscription = []
        self.cache = {}

    def connect(self):

        if not self.runtime.config.mqtt.connection.host:
            log.info('MQTT disabled')
            return None
        
        self.client = mqtt.Client(
            client_id=self.runtime.config.mqtt.connection.client_id,
            clean_session=False
        )

        if self.runtime.config.mqtt.connection.tls:
            self.client.tls_set()
        
        if self.runtime.config.mqtt.connection.tls_insecure:
            log.warning( 'Verification of server hostname in server certificate disabled!')
            log.warning( 'Use this only for testing, not for a real system!')
            self.client.tls_insecure_set( True)

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

        self.client.loop_start()
        
        self.runtime.config.mqtt.subscribe.subscribe_for_changes(self.subscription_changed)

    def subscription_changed(self):
        if self.subscription:
            unsub = [k[0] for k in self.subscription]
            for t in unsub:
                log.debug(f'Unsubscribing from "{topic}"')
            self.client.unsubscribe(unsub)
        
        topics = self.runtime.config.mqtt.subscribe.topics
        default_qos = self.runtime.config.mqtt.subscribe.qos
        self.subscription = [(topic, qos if qos is not None else default_qos) for topic, qos in topics]
        for topic, qos in self.subscription:
            log.debug( f'Subscribing to "{topic}" (QoS {qos:d})')
        self.client.subscribe(self.subscription)

    def on_connect(self, client, userdata, flags, rc):
        log.log(logging.INFO if not rc else logging.ERROR, mqtt.connack_string(rc))
        if rc:
            return None

        self.cache.clear()
        self.subscription.clear()
        self.subscription_changed()

    def on_disconnect(self, client, userdata, flags, rc):
        log.log( logging.INFO if not rc else logging.ERROR, "Unexpected disconnection")

    @PrintException
    def process_msg(self, client, userdata, message : mqtt.MQTTMessage):
        topic = message.topic
        payload = message.payload.decode("utf-8")
        log_msg.debug( f'{topic} ({message.qos}): {payload}')

        # try to cast to int/float
        try:
            payload = int(payload)
        except ValueError:
            try:
                payload = float(payload)
            except ValueError:
                pass
      
        __was = self.cache.get(topic, None)
        self.cache[topic] = payload
        
        HABApp.core.Events.post_event(topic, MqttUpdate(topic, payload), update_state=True)
        if __was is not None and __was != payload:
            HABApp.core.Events.post_event(topic, MqttChange(topic, payload))


    def publish(self, topic, payload=None, qos=0, retain=False):
        info = self.client.publish( topic, payload, qos, retain)
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            log.warning( f'Could not publish to "{topic}": {info.rc}! {info.}')