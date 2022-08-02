import logging
import logging.config
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Dict, List, Optional

import HABApp
from HABApp.config.config import CONFIG
from HABApp.config.errors import AbsolutePathExpected
from easyconfig.yaml import yaml_safe as _yaml_safe
from .buffered_logger import BufferedLogger
from .queue_handler import HABAppQueueHandler, SimpleQueue


def remove_memory_handler_from_cfg(cfg: dict, log: BufferedLogger):
    # find memory handlers
    m_handlers = {}
    for handler, handler_cfg in cfg.get('handlers', {}).items():
        if handler_cfg.get('class', '') == 'logging.handlers.MemoryHandler':
            log.error(f'"logging.handlers.MemoryHandler" is no longer required. Please remove from config ({handler})!')
            if 'target' in handler_cfg:
                m_handlers[handler] = handler_cfg['target']

    # remove them from config
    for h_name in m_handlers:
        cfg['handlers'].pop(h_name)
        log.warning(f'Removed {h_name:s} from handlers')

    # replace handlers in logger with target
    for logger_name, logger_cfg in cfg.get('loggers', {}).items():
        logger_handlers = logger_cfg.get('handlers', [])
        for i, logger_handler in enumerate(logger_handlers):
            replacement_handler = m_handlers.get(logger_handler)
            if replacement_handler is None:
                continue
            log.warning(f'Replaced {logger_handler} with {replacement_handler} for logger {logger_name}')
            logger_handlers[i] = replacement_handler


def get_logging_dict(path: Path, log: BufferedLogger) -> Optional[dict]:
    # config gets created on startup - if it gets deleted we do nothing here
    if not path.is_file():
        return None

    with path.open('r', encoding='utf-8') as file:
        cfg = _yaml_safe.load(file)  # type: Dict[str, Any]

    # fix filenames
    for handler, handler_cfg in cfg.get('handlers', {}).items():
        # migrate handler
        if handler_cfg.get('class', '-') == 'HABApp.core.lib.handler.MidnightRotatingFileHandler':
            dst = 'HABApp.config.logging.MidnightRotatingFileHandler'
            handler_cfg['class'] = dst
            log.warning(f'Replaced class for handler "{handler:s}" with {dst}')

        if 'filename' not in handler_cfg:
            continue

        # fix encoding for FileHandlers - we always log utf-8
        if 'file' in handler_cfg.get('class', '').lower():
            enc = handler_cfg.get('encoding', '')
            if enc != 'utf-8':
                handler_cfg['encoding'] = 'utf-8'

        # make Filenames absolute path in the log folder if not specified
        p = Path(handler_cfg['filename'])
        if not p.is_absolute():
            # Our log folder ist not yet converted to path -> it is not loaded
            if not CONFIG.directories.logging.is_absolute():
                raise AbsolutePathExpected()

            # Use defined parent folder
            p = (CONFIG.directories.logging / p).resolve()
            handler_cfg['filename'] = str(p)

    # remove memory handlers
    remove_memory_handler_from_cfg(cfg, log)

    # make file version optional for config file
    if 'version' not in cfg:
        cfg['version'] = 1
    else:
        log.warning('Entry "version" is no longer required in the logging configuration file')

    # Allow the user to set his own logging levels (with aliases)
    for level, alias in cfg.pop('levels', {}).items():
        if not isinstance(level, int):
            level = logging._nameToLevel[level]
        logging.addLevelName(level, str(alias))
        log.debug(f'Added custom Level "{str(alias)}" ({level})')

    return cfg


def rotate_files():
    for wr in logging._handlerList:
        handler = wr()  # weakref -> call it to get object

        # only rotate these types
        if not isinstance(handler, (RotatingFileHandler, TimedRotatingFileHandler)):
            continue

        # Rotate only if files have content
        logfile = Path(handler.baseFilename)
        if not logfile.is_file() or logfile.stat().st_size <= 10:
            continue

        try:
            handler.acquire()
            handler.flush()
            handler.doRollover()
        except Exception as e:
            HABApp.core.wrapper.process_exception(rotate_files, e)
        finally:
            handler.release()


def inject_log_buffer(cfg: dict, log: BufferedLogger):
    from HABApp.core.const.topics import TOPIC_EVENTS

    handler_cfg = cfg.setdefault('handlers', {})

    prefix = 'HABAppQueue_'

    # Check that the prefix is unique
    for handler_name in handler_cfg:
        if handler_name.startswith(prefix):
            raise ValueError(f'Handler may not start with {prefix:s}')

    # replace the event logs with the buffered one
    buffered_handlers = {}
    for log_name, log_cfg in cfg.get('loggers', {}).items():
        if not log_name.startswith(TOPIC_EVENTS):
            continue
        _handlers = {n: f'{prefix}{n}' for n in log_cfg['handlers']}
        buffered_handlers.update(_handlers)
        log_cfg['handlers'] = list(_handlers.values())

        # ensure propagate is disabled
        if log_cfg.get('propagate', False):
            log.warning(f'Propagate can not be set for {log_name}!')
        log_cfg['propagate'] = False

    if not buffered_handlers:
        return []

    handler_cfg = cfg.setdefault('handlers', {})
    q_handlers: List[HABAppQueueHandler] = []

    for handler_name, buffered_handler_name in buffered_handlers.items():
        q: SimpleQueue = SimpleQueue()
        handler_cfg[buffered_handler_name] = {'class': 'logging.handlers.QueueHandler', 'queue': q}

        qh = HABAppQueueHandler(q, handler_name, f'LogBuffer{handler_name:s}')
        q_handlers.append(qh)

    return q_handlers
