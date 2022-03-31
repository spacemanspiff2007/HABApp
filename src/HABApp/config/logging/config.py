import logging
import logging.config
import traceback
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

from easyconfig.yaml import yaml_safe as _yaml_safe

from HABApp.config.config import CONFIG
from HABApp.config.errors import AbsolutePathExpected

log = logging.getLogger('HABApp.Config')


def get_logging_dict(path: Path, log_msgs: List[Tuple[int, str]]) -> Optional[dict]:
    # config gets created on startup - if it gets deleted we do nothing here
    if not path.is_file():
        return None

    with path.open('r', encoding='utf-8') as file:
        cfg = _yaml_safe.load(file)  # type: Dict[str, Any]

    # fix filenames
    for handler, handler_cfg in cfg.get('handlers', {}).items():

        # fix encoding for FileHandlers - we always log utf-8
        if 'file' in handler_cfg.get('class', '').lower():
            enc = handler_cfg.get('encoding', '')
            if enc != 'utf-8':
                handler_cfg['encoding'] = 'utf-8'

        if 'filename' not in handler_cfg:
            continue

        # make Filenames absolute path in the log folder if not specified
        p = Path(handler_cfg['filename'])
        if not p.is_absolute():
            # Our log folder ist not yet converted to path -> it is not loaded
            if not CONFIG.directories.logging.is_absolute():
                raise AbsolutePathExpected()

            # Use defined parent folder
            p = (CONFIG.directories.logging / p).resolve()
            handler_cfg['filename'] = str(p)

    # make file version optional for config file
    if 'version' not in cfg:
        cfg['version'] = 1
    else:
        log_msgs.append((logging.INFO, 'Entry "version" is no longer required in the logging configuration file'))

    # Allow the user to set his own logging levels (with aliases)
    for level, alias in cfg.pop('levels', {}).items():
        if not isinstance(level, int):
            level = logging._nameToLevel[level]
        logging.addLevelName(level, str(alias))
        log_msgs.append((logging.DEBUG, f'Added custom Level "{str(alias)}" ({level})'))

    return cfg


def rotate_files():

    for wr in reversed(logging._handlerList[:]):
        handler = wr()  # weakref -> call it to get object

        # only rotate these types
        if not isinstance(handler, (RotatingFileHandler, TimedRotatingFileHandler)):
            continue

        # Rotate only if files have content
        logfile = Path(handler.baseFilename)
        if not logfile.is_file() or logfile.stat().st_size <= 0:
            continue

        try:
            handler.acquire()
            handler.doRollover()
        except Exception:
            for line in traceback.format_exc().splitlines():
                log.error(line)
        finally:
            handler.release()
