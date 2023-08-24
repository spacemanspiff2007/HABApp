import logging
from typing import Final as _Final

log: _Final      = logging.getLogger('HABApp.openhab.thing')
log_cfg: _Final  = log.getChild('cfg')
log_item: _Final = log.getChild('item')
