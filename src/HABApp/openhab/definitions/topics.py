try:
    from typing import Final as _Final
except ImportError:
    _Final = str


TOPIC_ITEMS: _Final = 'openHAB.Items'
TOPIC_THINGS: _Final = 'openHAB.Things'
