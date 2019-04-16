.. _ref_async_io:

asyncio
==================================

.. WARNING::
   | Please make sure you know what you are doing when using async functions!
   | If you have no asyncio experience please do not use this!
     The use of blocking calls in async functions may prevent HABApp from working properly!



async_http
------------------------------

Functions
""""""""""""""""""""""""""""""

.. py:class:: async_http
   
   .. py:method:: get(url: str, params: typing.Optional[Mapping[str, str]] = None, **kwargs: typing.Any)
       
       :param url: Request URL
       :param params: Mapping, iterable of tuple of key/value pairs (e.g. dict)
                      to be sent as parameters in the query string of the new request.
                      `Params example <https://docs.aiohttp.org/en/stable/client_quickstart.html#passing-parameters-in-urls>`_
       :param kwargs: See `aiohttp request <https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.request>`_ for further information
   
   
   .. py:method:: post(url: str, params: typing.Optional[Mapping[str, str]] = None, data: typing.Any = None, json: typing.Any = None, **kwargs: typing.Any)
       
       :param url: Request URL
       :param params: Mapping, iterable of tuple of key/value pairs (e.g. dict)
                      to be sent as parameters in the query string of the new request.
                      `Params example <https://docs.aiohttp.org/en/stable/client_quickstart.html#passing-parameters-in-urls>`_
       :param data: Dictionary, bytes, or file-like object to send in the body of the request
                    (optional)
       :param json: Any json compatible python object, json and data parameters could not be used at the same time.
                    (optional)
       :param kwargs: See `aiohttp request <https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.request>`_ for further information
   
   
   .. py:method:: put(url: str, params: typing.Optional[Mapping[str, str]] = None, data: typing.Any = None, json: typing.Any = None, **kwargs: typing.Any)
       
       :param url: Request URL
       :param params: Mapping, iterable of tuple of key/value pairs (e.g. dict)
                      to be sent as parameters in the query string of the new request.
                      `Params example <https://docs.aiohttp.org/en/stable/client_quickstart.html#passing-parameters-in-urls>`_
       :param data: Dictionary, bytes, or file-like object to send in the body of the request
                    (optional)
       :param json: Any json compatible python object, json and data parameters could not be used at the same time.
                    (optional)
       :param kwargs: See `aiohttp request <https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.request>`_ for further information
   
   
   .. py:method:: delete(url: str, params: typing.Optional[Mapping[str, str]] = None, **kwargs: typing.Any)
       
       :param url: Request URL
       :param params: Mapping, iterable of tuple of key/value pairs (e.g. dict)
                      to be sent as parameters in the query string of the new request.
                      `Params example <https://docs.aiohttp.org/en/stable/client_quickstart.html#passing-parameters-in-urls>`_
       :param kwargs: See `aiohttp request <https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.request>`_ for further information
   

Examples
""""""""""""""""""""""""""""""

Example::

    async with self.async_http.get('http://httpbin.org/get') as resp:
        print(resp.status)
        print(await resp.text())
