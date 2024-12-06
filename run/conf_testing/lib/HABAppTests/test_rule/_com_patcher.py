import json
import logging
import pprint
from collections.abc import Callable
from types import ModuleType, TracebackType
from typing import Any, Final

from pytest import MonkeyPatch

import HABApp.mqtt.connection.publish
import HABApp.mqtt.connection.subscribe
import HABApp.openhab.connection.handler
import HABApp.openhab.connection.handler.func_async
import HABApp.openhab.process_events
from HABApp.config import CONFIG


class PatcherName:
    def __init__(self, header: str) -> None:
        self.header = header
        self.logged = False


class BasePatcher:
    @staticmethod
    def create_name(header: str) -> PatcherName:
        return PatcherName(header)

    def __init__(self, name: PatcherName, logger_name: str) -> None:
        self._log: Final = logging.getLogger('Com').getChild(logger_name)
        self.name: Final = name
        self.monkeypatch: Final = MonkeyPatch()

    def log(self, msg: str) -> None:
        if not self.name.logged:
            self._log.debug('')
            self._log.debug(self.name.header)
            self.name.logged = True
        self._log.debug(msg)

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None,
                 exc_tb: TracebackType | None) -> bool:

        self.monkeypatch.undo()
        return False


def shorten_url(url: str) -> str:
    url = str(url)
    cfg = CONFIG.openhab.connection.url
    if url.startswith(cfg):
        return url[len(cfg):]
    return url


class RestPatcher(BasePatcher):

    def __init__(self, name: str) -> None:
        super().__init__(name, 'Rest')

    def wrap_http(self, to_call):
        async def resp_wrap(*args, **kwargs):

            resp = await to_call(*args, **kwargs)

            out = ''
            if kwargs.get('json') is not None:
                out = f' {kwargs["json"]}'
            if kwargs.get('data') is not None:
                out = f' "{kwargs["data"]}"'

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

    def __enter__(self) -> None:
        m = self.monkeypatch

        # http functions
        to_patch: Final[tuple[tuple[ModuleType, tuple[str, ...]]], ...] = (
            (HABApp.openhab.connection.handler, ('get', 'put', 'post', 'delete')),
            (HABApp.openhab.connection.handler.func_async, ('get', 'put', 'post', 'delete')),
            (HABApp.openhab.connection.plugins.out, ('put', 'post')),
        )

        for module, methods in to_patch:
            for name in methods:
                m.setattr(module, name, self.wrap_http(getattr(module, name)))


class SsePatcher(BasePatcher):

    def __init__(self, name: str) -> None:
        super().__init__(name, 'SSE')

    def wrap_sse(self, to_wrap: Callable[[dict], Any]) -> Callable[[dict], Any]:
        def new_call(_dict: dict) -> Any:
            self.log(f'{"SSE":^6s} {_dict}')
            return to_wrap(_dict)
        return new_call

    def __enter__(self) -> None:
        module = HABApp.openhab.process_events
        self.monkeypatch.setattr(module, 'get_event', self.wrap_sse(module.get_event))


class MqttPatcher(BasePatcher):

    def __init__(self, name: str) -> None:
        super().__init__(name, 'Mqtt')

    def wrap_msg(self, func: Callable[[str, Any, bool], Any]) -> Callable[[str, Any, bool], Any]:
        def new_call(topic: str, payload: Any, retain: bool) -> Any:
            self.log(f'{"MSG":^6s} {"R" if retain else " "}  {topic} {payload}')
            return func(topic, payload, retain)
        return new_call

    def pub_msg(self, func: Callable[[str, Any, int, bool], Any]) -> Callable[[str, Any, int, bool], Any]:
        async def wrapped_publish(topic: str, payload: Any, qos: int = 0, retain: bool = False) -> Any:
            self.log(f'{"PUB":^6s} {"R" if retain else " "}{qos:d} {topic} {payload}')
            return await func(topic, payload, qos, retain)
        return wrapped_publish

    def __enter__(self) -> None:
        m = self.monkeypatch

        module = HABApp.mqtt.connection.subscribe
        m.setattr(module, 'msg_to_event', self.wrap_msg(module.msg_to_event))

        obj = HABApp.mqtt.connection.publish.PUBLISH_HANDLER.plugin_connection.context
        m.setattr(obj, 'publish', self.pub_msg(obj.publish))
