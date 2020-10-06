import json
import logging
import pprint

import HABApp.openhab.connection_handler.http_connection
from HABApp.openhab.connection_handler.http_connection import HTTP_PREFIX

FUNC_PATH = HABApp.openhab.connection_handler.func_async


def shorten_url(url: str):
    url = str(url)
    if url.startswith(HTTP_PREFIX):
        return url[len(HTTP_PREFIX):]
    return url


class RestPatcher:
    def __init__(self, name):
        self.log = logging.getLogger('HABApp.Rest')
        self.log.debug('')
        self.log.debug(f'{name}:')

    def wrap(self, to_call):
        async def resp_wrap(*args, **kwargs):

            resp = await to_call(*args, **kwargs)

            out = ''
            if kwargs.get('json'):
                out = f' {kwargs["json"]}'
            if kwargs.get('data'):
                out = f' "{kwargs["data"]}"'
            self.log.debug(f'{resp.request_info.method:^6s} {shorten_url(resp.request_info.url)} ({resp.status}){out}')

            def wrap_content(content_func):
                async def content_func_wrap(*cargs, **ckwargs):
                    t = await content_func(*cargs, **ckwargs)

                    if isinstance(t, (dict, list)):
                        txt = json.dumps(t, indent=2)
                    else:
                        txt = pprint.pformat(t, indent=2)

                    lines = txt.splitlines()
                    for i, l in enumerate(lines):
                        self.log.debug(f'{"->" if not i else "":^6s} {l}')

                    return t
                return content_func_wrap

            resp.text = wrap_content(resp.text)
            resp.json = wrap_content(resp.json)
            return resp
        return resp_wrap

    def __enter__(self):
        self._get = FUNC_PATH.get
        self._put = FUNC_PATH.put
        self._post = FUNC_PATH.post
        self._delete = FUNC_PATH.delete

        FUNC_PATH.get = self.wrap(self._get)
        FUNC_PATH.put = self.wrap(self._put)
        FUNC_PATH.post = self.wrap(self._post)
        FUNC_PATH.delete = self.wrap(self._delete)

    def __exit__(self, exc_type, exc_val, exc_tb):
        FUNC_PATH.get = self._get
        FUNC_PATH.put = self._put
        FUNC_PATH.post = self._post
        FUNC_PATH.delete = self._delete

        return False
