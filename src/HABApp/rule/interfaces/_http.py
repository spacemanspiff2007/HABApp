from typing import Any, Optional, Mapping

import aiohttp

import HABApp
from HABApp.core.const.json import dump_json


CLIENT: Optional[aiohttp.ClientSession] = None


async def create_client():
    global CLIENT
    assert CLIENT is None

    CLIENT = aiohttp.ClientSession(json_serialize=dump_json, loop=HABApp.core.const.loop)

    from HABApp.runtime import shutdown
    shutdown.register_func(CLIENT.close, msg='Closing generic http connection')


def get(url: str, params: Optional[Mapping[str, str]] = None, **kwargs: Any)\
        -> aiohttp.client._RequestContextManager:
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
    assert CLIENT is not None
    return CLIENT.get(url, params=params, **kwargs)


def post(url: str, params: Optional[Mapping[str, str]] = None,
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
    assert CLIENT is not None
    return CLIENT.post(url, params=params, data=data, json=json, **kwargs)


def put(url: str, params: Optional[Mapping[str, str]] = None,
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
    assert CLIENT is not None
    return CLIENT.put(url, params=params, data=data, json=json, **kwargs)


def delete(url: str, params: Optional[Mapping[str, str]] = None, **kwargs: Any)\
        -> aiohttp.client._RequestContextManager:
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
    assert CLIENT is not None
    return CLIENT.delete(url, params=params, **kwargs)


def get_client_session() -> aiohttp.ClientSession:
    """Return the aiohttp
    `client session object <https://docs.aiohttp.org/en/stable/client_reference.html#client-session>`_
    for use in aiohttp libraries

    :return: session object
    """
    assert CLIENT is not None
    return CLIENT
