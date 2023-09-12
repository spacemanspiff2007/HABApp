import json
import logging
import pprint

from pytest import MonkeyPatch

import HABApp.openhab.connection.handler
import HABApp.openhab.connection.handler.func_async
import HABApp.openhab.process_events
from HABApp.config import CONFIG


def shorten_url(url: str):
    url = str(url)
    cfg = CONFIG.openhab.connection.url
    if url.startswith(cfg):
        return url[len(cfg):]
    return url


class RestPatcher:
    def __init__(self, name: str):
        self.name = name
        self.logged_name = False
        self._log = logging.getLogger('HABApp.Rest')

        self.monkeypatch = MonkeyPatch()

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

            if resp.status >= 300 and kwargs.get('log_404', True):
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
        m = self.monkeypatch

        # event handler
        module = HABApp.openhab.process_events
        m.setattr(module, 'get_event', self.wrap_sse(module.get_event))

        # http functions
        for module in (HABApp.openhab.connection.handler, HABApp.openhab.connection.handler.func_async,):
            for name in ('get', 'put', 'post', 'delete'):
                m.setattr(module, name, self.wrap(getattr(module, name)))

        # additional communication
        module = HABApp.openhab.connection.plugins.out
        m.setattr(module, 'put', self.wrap(getattr(module, 'put')))
        m.setattr(module, 'post', self.wrap(getattr(module, 'post')))

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.monkeypatch.undo()
        return False
