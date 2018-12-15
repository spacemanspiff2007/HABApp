import logging
import paho.mqtt.client as mqtt


import HABApp
from HABApp.util import PrintException

log = logging.getLogger('HABApp.mqtt.connection')
log_msg = logging.getLogger('HABApp.mqtt.messages')

class MqttConnection:
    def __init__(self, parent):
        assert isinstance(parent, HABApp.Runtime)
        self.runtime: HABApp.Runtime = parent

        self.connected = False
        self.client : mqtt.Client = None

        self.subscription = []
        self.cache = {}
        
        self.runtime.config.mqtt.subscribe.subscribe_for_changes(self.subscription_changed)
        self.runtime.config.mqtt.connection.subscribe_for_changes(self.connect)


    def connect(self):
        if not self.runtime.config.mqtt.connection.host:
            log.info('MQTT disabled')
            return None

        if self.connected:
            log.info('disconnecting')
            self.client.disconnect()
        
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
        

    @PrintException
    def subscription_changed(self):
        if not self.connected:
            return None
        
        if self.subscription:
            unsubscribe = [k[0] for k in self.subscription]
            for t in unsubscribe:
                log.debug(f'Unsubscribing from "{t}"')
            self.client.unsubscribe(unsubscribe)
        
        topics = self.runtime.config.mqtt.subscribe.topics
        default_qos = self.runtime.config.mqtt.subscribe.qos
        self.subscription = [(topic, qos if qos is not None else default_qos) for topic, qos in topics]
        for topic, qos in self.subscription:
            log.debug( f'Subscribing to "{topic}" (QoS {qos:d})')
        self.client.subscribe(self.subscription)

    @PrintException
    def on_connect(self, client, userdata, flags, rc):
        log.log(logging.INFO if not rc else logging.ERROR, mqtt.connack_string(rc))
        if rc:
            return None
        self.connected = True

        self.cache.clear()
        self.subscription.clear()
        self.subscription_changed()

    @PrintException
    def on_disconnect(self, client, userdata, flags, rc):
        log.log( logging.INFO if not rc else logging.ERROR, "Unexpected disconnection")
        self.connected = False

    @PrintException
    def process_msg(self, client, userdata, message : mqtt.MQTTMessage):
        topic = message.topic
        payload = message.payload.decode("utf-8")
        
        if log_msg.isEnabledFor(logging.DEBUG):
            log_msg._log( logging.DEBUG,  f'{topic} ({message.qos}): {payload}', [])

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
        
        HABApp.core.Events.post_event(topic, HABApp.core.ValueUpdateEvent(topic, payload))
        if __was is not None and __was != payload:
            HABApp.core.Events.post_event(topic, HABApp.core.ValueChangeEvent(topic, payload, __was))

    def publish(self, topic, payload, qos, retain):
        
        if qos is None:
            qos = self.runtime.config.mqtt.publish.qos
        if retain is None:
            retain = self.runtime.config.mqtt.publish.retain

        info = self.client.publish( topic, payload, qos, retain)
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            log.warning( f'Could not publish to "{topic}": {mqtt.error_string(info.rc)}')
