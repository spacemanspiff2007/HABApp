import json
import logging
import pprint

import HABApp.openhab.connection_handler.http_connection
import HABApp.openhab.connection_logic.connection
from HABApp.openhab.connection_handler.http_connection import HTTP_PREFIX

FUNC_PATH = HABApp.openhab.connection_handler.func_async
SSE_PATH = HABApp.openhab.connection_logic.connection


def shorten_url(url: str):
    url = str(url)
    if url.startswith(HTTP_PREFIX):
        return url[len(HTTP_PREFIX):]
    return url


class RestPatcher:
    def __init__(self, name: str):
        self.name = name
        self.logged_name = False
        self._log = logging.getLogger('HABApp.Rest')

    def log(self, msg: str):
        # Log name when we log the first message
        if not self.logged_name:
            self.logged_name = True
            self._log.debug('')
            self._log.debug(f'{self.name}:')

        self._log.debug(msg)

    def wrap(self, to_call):
        async def resp_wrap(*args, **kwargs):

            resp = await to_call(*args, **kwargs)

            out = ''
            if kwargs.get('json') is not None:
                out = f' {kwargs["json"]}'
            if kwargs.get('data') is not None:
                out = f' "{kwargs["data"]}"'

            # Log name when we log the first message
            if not self.logged_name:
                self.logged_name = True
                self.log('')
                self.log(f'{self.name}:')

            self.log(
                f'{resp.request_info.method:^6s} {shorten_url(resp.request_info.url)} ({resp.status}){out}'
            )

            if resp.status >= 300 and kwargs['log_404']:
                self.log(f'{"":6s} Header request : {resp.request_info.headers}')
                self.log(f'{"":6s} Header response: {resp.headers}')

            def wrap_content(content_func):
                async def content_func_wrap(*cargs, **ckwargs):
                    t = await content_func(*cargs, **ckwargs)

                    if isinstance(t, (dict, list)):
                        txt = json.dumps(t, indent=2)
                    else:
                        txt = pprint.pformat(t, indent=2)

                    lines = txt.splitlines()
                    for i, l in enumerate(lines):
                        self.log(f'{"->" if not i else "":^6s} {l}')

                    return t
                return content_func_wrap

            resp.text = wrap_content(resp.text)
            resp.json = wrap_content(resp.json)
            return resp
        return resp_wrap

    def wrap_sse(self, to_wrap):
        def new_call(_dict):
            self.log(f'{"SSE":^6s} {_dict}')
            return to_wrap(_dict)
        return new_call

    def __enter__(self):
        self._get = FUNC_PATH.get
        self._put = FUNC_PATH.put
        self._post = FUNC_PATH.post
        self._delete = FUNC_PATH.delete

        self._sse = SSE_PATH.get_event

        FUNC_PATH.get = self.wrap(self._get)
        FUNC_PATH.put = self.wrap(self._put)
        FUNC_PATH.post = self.wrap(self._post)
        FUNC_PATH.delete = self.wrap(self._delete)

        SSE_PATH.get_event = self.wrap_sse(self._sse)

    def __exit__(self, exc_type, exc_val, exc_tb):
        FUNC_PATH.get = self._get
        FUNC_PATH.put = self._put
        FUNC_PATH.post = self._post
        FUNC_PATH.delete = self._delete

        SSE_PATH.get_event = self._sse
        return False
