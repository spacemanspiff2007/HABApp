import logging
from typing import Tuple, Any, Optional

from aiomqtt import Message

from HABApp.core.const.json import load_json
from HABApp.core.const.log import TOPIC_EVENTS
from HABApp.core.wrapper import process_exception

log = logging.getLogger(f'{TOPIC_EVENTS}.mqtt')


def get_msg_payload(msg: Message) -> Tuple[Optional[str], Any]:
    try:
        topic = msg.topic.value
        raw = msg.payload

        try:
            val = raw.decode("utf-8")
        except UnicodeDecodeError:
            # Payload ist a byte stream
            if log.isEnabledFor(logging.DEBUG):
                log._log(logging.DEBUG, f'{topic} ({msg.qos}): {raw[:20]}...', [])
            return topic, raw

        if log.isEnabledFor(logging.DEBUG):
            log._log(logging.DEBUG, f'{topic} ({msg.qos}): {val}', [])

        # None
        if val == 'none' or val == 'None':
            return topic, None

        # bool
        if val == 'true' or val == 'True':
            return topic, True
        if val == 'false' or val == 'False':
            return topic, False

        # int
        if val.isdecimal():
            return topic, int(val)

        # json list/dict
        if val.startswith('{') and val.endswith('}') or val.startswith('[') and val.endswith(']'):
            try:
                return topic, load_json(val)
            except ValueError:
                return topic, val

        # float or str
        try:
            return topic, float(val)
        except ValueError:
            return topic, val
    except Exception as e:
        process_exception(get_msg_payload, e, logger=log)
        return None, None
