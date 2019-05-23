import unittest

# from .context import HABApp
from HABApp.openhab.http_connection import HttpConnection, HttpConnectionEventHandler


class TestEventHandler(HttpConnectionEventHandler):
    pass


class TestCases(unittest.TestCase):

    def setUp(self) -> None:
        self.con = HttpConnection(TestEventHandler(), None)

    def test_aiohttp_sse_client_exceptions(self):

        list = [ConnectionError, ConnectionRefusedError, ConnectionAbortedError]
        for k in list:
            try:
                raise k()
            except Exception as e:
                disconnect = self.con._is_disconnect_exception(e)
                self.assertTrue(disconnect)


if __name__ == '__main__':
    unittest.main()
