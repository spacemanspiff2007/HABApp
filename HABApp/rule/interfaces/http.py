from typing import Any, Optional, Mapping

import aiohttp

from HABApp.core.const import loop
from HABApp.core.const.json import dump_json


class AsyncHttpConnection:

    def __init__(self):
        self.__client: aiohttp.ClientSession = None

    async def create_client(self):
        self.__client = aiohttp.ClientSession(json_serialize=dump_json, loop=loop)

    def get(self, url: str, params: Optional[Mapping[str, str]] = None, **kwargs: Any)\
            -> aiohttp.client._RequestContextManager:
        """http get request

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
        return self.__client.get(url, params=params, **kwargs)

    def post(self, url: str, params: Optional[Mapping[str, str]] = None,
             data: Any = None, json: Any = None, **kwargs: Any) -> aiohttp.client._RequestContextManager:
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
        return self.__client.post(url, params=params, data=data, json=json, **kwargs)

    def put(self, url: str, params: Optional[Mapping[str, str]] = None,
            data: Any = None, json: Any = None, **kwargs: Any) -> aiohttp.client._RequestContextManager:
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
        return self.__client.put(url, params=params, data=data, json=json, **kwargs)

    def delete(self, url: str, params: Optional[Mapping[str, str]] = None, **kwargs: Any)\
            -> aiohttp.client._RequestContextManager:

        return self.__client.delete(url, params=params, **kwargs)

    def get_client_session(self) -> aiohttp.ClientSession:
        """Return the aiohttp
        `client session object <https://docs.aiohttp.org/en/stable/client_reference.html#client-session>`_
        for use in aiohttp libraries

        :return: session object
        """
        return self.__client
