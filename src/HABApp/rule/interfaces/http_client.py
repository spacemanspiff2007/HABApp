import logging
from collections.abc import AsyncGenerator, Mapping
from typing import Any, Final

import aiohttp
from aiohttp.client import _RequestContextManager

from HABApp.core.const.json import dump_json
from HABApp.core.const.log import TOPIC_SHUTDOWN
from HABApp.core.provider import HABAPP_PROVIDER


class HABAppHttpClient:
    def __init__(self, client: aiohttp.ClientSession) -> None:
        self._client: Final = client

    def get(self, url: str, params: Mapping[str, str] | None = None, **kwargs: Any) -> _RequestContextManager:
        """http get request

        :param url: Request URL
        :param params: Mapping, iterable of tuple of key/value pairs (e.g. dict)
                       to be sent as parameters in the query string of the new request.
                       `Params example
                       <https://docs.aiohttp.org/en/stable/client_quickstart.html#passing-parameters-in-urls>`_
        :param kwargs: See `aiohttp request <https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.request>`_
                       for further possible kwargs
        :return: awaitable
        """
        return self._client.get(url, params=params, **kwargs)

    def post(self, url: str, params: Mapping[str, str] | None = None,
             data: Any = None, json: Any = None, **kwargs: Any) -> _RequestContextManager:
        """http post request

        :param url: Request URL
        :param params: Mapping, iterable of tuple of key/value pairs (e.g. dict)
                       to be sent as parameters in the query string of the new request.
                       `Params example
                       <https://docs.aiohttp.org/en/stable/client_quickstart.html#passing-parameters-in-urls>`_
        :param data: Dictionary, bytes, or file-like object to send in the body of the request
                     (optional)
        :param json: Any json compatible python object, json and data parameters could not be used at the same time.
                     (optional)
        :param kwargs: See `aiohttp request <https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.request>`_
                       for further possible kwargs
        :return: awaitable
        """
        return self._client.post(url, params=params, data=data, json=json, **kwargs)

    def put(self, url: str, params: Mapping[str, str] | None = None,
            data: Any = None, json: Any = None, **kwargs: Any) -> _RequestContextManager:
        """http put request

        :param url: Request URL
        :param params: Mapping, iterable of tuple of key/value pairs (e.g. dict)
                       to be sent as parameters in the query string of the new request.
                       `Params example
                       <https://docs.aiohttp.org/en/stable/client_quickstart.html#passing-parameters-in-urls>`_
        :param data: Dictionary, bytes, or file-like object to send in the body of the request
                     (optional)
        :param json: Any json compatible python object, json and data parameters could not be used at the same time.
                     (optional)
        :param kwargs: See `aiohttp request <https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.request>`_
                       for further possible kwargs
        :return: awaitable
        """
        return self._client.put(url, params=params, data=data, json=json, **kwargs)

    def delete(self, url: str, params: Mapping[str, str] | None = None,
               **kwargs: Any) -> _RequestContextManager:
        """http delete request

        :param url: Request URL
        :param params: Mapping, iterable of tuple of key/value pairs (e.g. dict)
                       to be sent as parameters in the query string of the new request.
                       `Params example
                       <https://docs.aiohttp.org/en/stable/client_quickstart.html#passing-parameters-in-urls>`_
        :param kwargs: See `aiohttp request <https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.request>`_
                       for further possible kwargs
        :return: awaitable
        """
        return self._client.delete(url, params=params, **kwargs)

    def get_client_session(self) -> aiohttp.ClientSession:
        """Return the aiohttp
        `client session object <https://docs.aiohttp.org/en/stable/client_reference.html#client-session>`_
        for use in aiohttp libraries

        :return: session object
        """
        return self._client


@HABAPP_PROVIDER.register
async def create_client() -> AsyncGenerator[HABAppHttpClient, Any]:

    client = aiohttp.ClientSession(json_serialize=dump_json)

    yield HABAppHttpClient(client)

    logging.getLogger(TOPIC_SHUTDOWN).debug('Closing generic http connections')
    await client.close()
