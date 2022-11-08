import logging
import re
from typing import Dict, Iterator, List, Any

from HABApp.openhab.definitions.helpers.log_table import Table
from ._log import log

THING_ALIAS: Dict[str, str] = {
    'thing_uid': 'UID',
    'thing_type': 'thingTypeUID',
    'thing_location': 'location',
    'thing_label': 'label',
    'bridge_uid': 'bridgeUID',
    'editable': 'editable',
}

CHANNEL_ALIAS: Dict[str, str] = {
    'channel_uid': 'uid',
    'channel_type': 'channelTypeUID',
    'channel_label': 'label',
    'channel_kind': 'kind',
    # 'channel_description': 'description',
}


class BaseFilter:
    KEYS: Dict[str, str]

    def __init__(self, key: str, regex: str):
        self.key = key
        try:
            self.alias = self.KEYS[key]
        except KeyError:
            raise ValueError(f'Key {key} can not be used as a filter! Available: {", ".join(self.KEYS)}') from None

        try:
            self.search = re.compile(regex, re.IGNORECASE)
        except re.error as e:
            raise ValueError(f'Could not compile regex "{regex}": {e}') from None

    def matches(self, _dict: dict, test: bool) -> bool:
        v = _dict.get(self.alias)
        if v is None:
            return False
        m = self.search.fullmatch(v) is not None
        if m:
            log.log(
                logging.DEBUG if not test else logging.INFO,
                f'{self.key} "{self.search.pattern}" matches for '
                f'{_dict.get("UID", _dict.get("uid", "?UID NOT FOUND?"))}!'
            )
        return m

    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.key}", "{self.search.pattern}">'


class ThingFilter(BaseFilter):
    KEYS = THING_ALIAS


class ChannelFilter(BaseFilter):
    KEYS = CHANNEL_ALIAS


def apply_filters(filters: List[BaseFilter], iterable: List[Dict[str, str]], test: bool) -> Iterator[Dict[str, Any]]:
    return filter(lambda n: all(map(lambda filter: filter.matches(n, test), filters)), iterable)


def log_overview(data: List[dict], aliases: Dict[str, str], heading=''):
    table = Table(heading)
    for k in aliases:
        table.add_column(k, align='<')
    for _item in data:
        add = {}
        for k, alias in aliases.items():
            v = _item.get(alias, '')
            # sometimes the key is there but the value is None
            if v is None:
                v = ''
            add[k] = v
        table.add_dict(add)
    for line in table.get_lines(sort_columns=['thing_type'] if 'thing_type' in table.columns else None):
        log.info(line)
