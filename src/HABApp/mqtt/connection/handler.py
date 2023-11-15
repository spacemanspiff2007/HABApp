from __future__ import annotations

from aiomqtt import Client, TLSParameters

from HABApp.config import CONFIG
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.connections._definitions import CONNECTION_HANDLER_NAME

from HABApp.core.internals import uses_post_event, uses_get_item, uses_item_registry
from HABApp.mqtt.connection.connection import CONTEXT_TYPE, MqttConnection

post_event = uses_post_event()
get_item = uses_get_item()
Items = uses_item_registry()


class ConnectionHandler(BaseConnectionPlugin[MqttConnection]):
    def __init__(self):
        super().__init__(name=CONNECTION_HANDLER_NAME)

    async def on_setup(self, connection: MqttConnection):
        log = connection.log
        config = CONFIG.mqtt.connection

        if not config.host:
            log.info('MQTT disabled')
            connection.status_from_setup_to_disabled()
            return None

        tls_insecure: bool | None = None
        tls_ca_cert: str | None = None
        if tls_enabled := config.tls.enabled:
            log.debug("TLS enabled")

            # add option to specify tls certificate
            ca_cert = config.tls.ca_cert
            if ca_cert is not None and ca_cert.name:
                if not ca_cert.is_file():
                    log.error(f'Ca cert file does not exist: {ca_cert}')
                    # don't connect without the properly set certificate
                    connection.set_error()
                    return None

                log.debug(f"CA cert path: {ca_cert}")
                tls_ca_cert = str(ca_cert)

            # we can only set tls_insecure if we have a tls connection
            if config.tls.insecure:
                log.warning('Verification of server hostname in server certificate disabled!')
                log.warning('Use this only for testing, not for a real system!')
                tls_insecure = True

        connection.context = Client(
            hostname=config.host, port=config.port,
            username=config.user if config.user else None, password=config.password if config.password else None,
            client_id=config.client_id,

            tls_insecure=tls_insecure,
            tls_params=None if not tls_enabled else TLSParameters(ca_certs=tls_ca_cert),

            # clean_session=False
        )

    async def on_connecting(self, connection: MqttConnection, context: CONTEXT_TYPE):
        assert context is not None

        connection.log.info(f'Connecting to {context._hostname}:{context._port}')
        await context.__aenter__()
        connection.log.info('Connection successful')

    async def on_disconnected(self, connection: MqttConnection, context: CONTEXT_TYPE):
        assert context is not None

        connection.log.info('Disconnected')
        await context.__aexit__(None, None, None)


CONNECTION_HANDLER = ConnectionHandler()
