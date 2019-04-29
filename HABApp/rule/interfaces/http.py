import aiohttp
import ujson
from typing import Any, Optional, Mapping


class AsyncHttpConnection:

    def __init__(self):
        self.__client = aiohttp.ClientSession(json_serialize=ujson.dumps)

    def get(self, url: str, params: Optional[Mapping[str, str]] = None, **kwargs: Any):

        return self.__client.get(url, params=params, **kwargs)

    def post(self, url: str, params: Optional[Mapping[str, str]] = None,
             data: Any = None, json: Any = None, **kwargs: Any):

        return self.__client.post(url, params=params, data=data, json=json, **kwargs)

    def put(self, url: str, params: Optional[Mapping[str, str]] = None,
            data: Any = None, json: Any = None, **kwargs: Any):
        """

        :param url: Request URL
        :param params: Mapping, iterable of tuple of key/value pairs (e.g. dict)
                       to be sent as parameters in the query string of the new request
        :param data: Dictionary, bytes, or file-like object to send in the body of the request (optional)
        :param json: Any json compatible python object (optional).
                     json and data parameters could not be used at the same time.
        :param kwargs:
        :return:
        """
        return self.__client.put(url, params=params, data=data, json=json, **kwargs)

    def delete(self, url: str, params: Optional[Mapping[str, str]] = None, **kwargs: Any):

        return self.__client.delete(url, params=params, **kwargs)
