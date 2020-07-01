from HABApp.openhab.connection_handler.http_connection import is_disconnect_exception


def test_aiohttp_sse_client_exceptions():
    list = [ConnectionError, ConnectionRefusedError, ConnectionAbortedError]
    for k in list:
        try:
            raise k()
        except Exception as e:
            assert is_disconnect_exception(e)
