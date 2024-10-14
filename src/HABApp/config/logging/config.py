import logging
import logging.config
from pathlib import Path
from queue import Queue
from typing import Any

from easyconfig.yaml import yaml_safe as _yaml_safe

from HABApp.config.config import CONFIG
from HABApp.config.errors import AbsolutePathExpected
from HABApp.config.logging import rotate_file
from HABApp.core.const.const import PYTHON_312, PYTHON_313
from HABApp.core.const.log import TOPIC_EVENTS

from .buffered_logger import BufferedLogger
from .queue_handler import HABAppQueueHandler, SimpleQueue


def fix_old_logger_location(handlers_cfg: dict, log: BufferedLogger) -> None:
    src = 'HABApp.core.lib.handler.MidnightRotatingFileHandler'
    dst = 'HABApp.config.logging.MidnightRotatingFileHandler'

    # fix filenames
    for handler, cfg in handlers_cfg.items():
        # migrate handler
        if cfg.get('class', '-') == src:
            cfg['class'] = dst
            log.warning(f'Replaced class for handler "{handler:s}" with {dst:s}')


def fix_log_filenames(handlers_cfg: dict) -> None:
    for cfg in handlers_cfg.values():
        if (filename := cfg.get('filename')) is None:
            continue

        # fix encoding for FileHandlers - we always log utf-8
        if 'file' in cfg.get('class', '').lower() and cfg.get('encoding', '') != 'utf-8':
            cfg['encoding'] = 'utf-8'

        # make Filenames absolute path in the log folder if not specified
        p = Path(filename)
        if not p.is_absolute():
            # Our log folder ist not yet converted to path -> it is not loaded
            if not CONFIG.directories.logging.is_absolute():
                raise AbsolutePathExpected()

            # Use defined parent folder
            p = (CONFIG.directories.logging / p).resolve()
            cfg['filename'] = str(p)


def remove_memory_handler_from_cfg(handlers_cfg: dict, loggers_cfg: dict, log: BufferedLogger) -> None:
    # find memory handlers
    memory_targets = {}
    for handler, handler_cfg in handlers_cfg.items():
        if handler_cfg.get('class', '') == 'logging.handlers.MemoryHandler':
            log.error(f'"logging.handlers.MemoryHandler" is no longer required. Please remove from config ({handler})!')
            if 'target' in handler_cfg:
                memory_targets[handler] = handler_cfg['target']

    # remove them from config
    for h_name in memory_targets:
        handlers_cfg.pop(h_name)
        log.warning(f'Removed {h_name:s} from handlers')

    # replace handlers in logger with target
    for logger_name, logger_cfg in loggers_cfg.items():
        logger_handlers = logger_cfg.get('handlers', [])
        for i, logger_handler in enumerate(logger_handlers):
            if (replacement_handler := memory_targets.get(logger_handler)) is None:
                continue
            log.warning(f'Replaced {logger_handler} with {replacement_handler} for logger {logger_name}')
            logger_handlers[i] = replacement_handler


def load_logging_file(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None

    with path.open('r', encoding='utf-8') as file:
        cfg: dict[str, Any] = _yaml_safe.load(file)
    return cfg


def rotate_handler_files(handlers_cfg: dict) -> None:
    for cfg in handlers_cfg.values():
        if (filename := cfg.get('filename')) is None:
            continue
        if (backup_count := cfg.get('backupCount')) is None:
            continue
        file = Path(filename)

        # If the file is empty we do not rotate
        if not file.is_file() or file.stat().st_size <= 10:  # noqa: PLR2004
            continue

        rotate_file(file, backup_count)


def inject_queue_handler(handlers_cfg: dict, loggers_cfg: dict, log: BufferedLogger) -> list[HABAppQueueHandler]:
    if not CONFIG.habapp.logging.use_buffer:
        return []

    prefix = 'HABAppQueue_'

    # Check that the prefix is unique
    for handler_name in handlers_cfg:
        if handler_name.startswith(prefix):
            msg = f'Handler may not start with {prefix:s}'
            raise ValueError(msg)

    # replace the event logs with the buffered one
    buffered_handlers = {}
    for log_name, log_cfg in loggers_cfg.items():
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

    q_handlers: list[HABAppQueueHandler] = []

    for handler_name, buffered_handler_name in buffered_handlers.items():
        # https://github.com/python/cpython/issues/124653
        if PYTHON_313:
            q: SimpleQueue = SimpleQueue()
        elif PYTHON_312:
            q = Queue()
        else:
            q: SimpleQueue = SimpleQueue()
        handlers_cfg[buffered_handler_name] = {'class': 'logging.handlers.QueueHandler', 'queue': q}

        qh = HABAppQueueHandler(q, handler_name, f'LogBuffer{handler_name:s}')
        q_handlers.append(qh)

    return q_handlers


def process_custom_levels(cfg: dict[str, Any], log: BufferedLogger) -> None:
    for level, alias in cfg.pop('levels', {}).items():
        if not isinstance(level, int):
            # noinspection PyProtectedMember
            level = logging._nameToLevel[level]  # noqa: PLW2901
        logging.addLevelName(level, str(alias))
        log.debug(f'Added custom log level "{alias!s}" ({level})')


def get_logging_dict(cfg: dict[str, Any] | None,
                     log: BufferedLogger | logging.Logger) -> tuple[dict[str, Any], list[HABAppQueueHandler]]:

    # make file version optional for config file
    if 'version' in cfg:
        log.warning('Entry "version" is no longer required in the logging configuration file')
    else:
        cfg['version'] = 1

    handlers_cfg = cfg.get('handlers', {})
    loggers_cfg = cfg.get('loggers', {})

    fix_old_logger_location(handlers_cfg, log)
    fix_log_filenames(handlers_cfg)
    remove_memory_handler_from_cfg(handlers_cfg, loggers_cfg, log)

    # Rotate files before opening the handlers
    rotate_handler_files(handlers_cfg)

    # Allow the user to set his own logging levels (with aliases)
    process_custom_levels(cfg, log)

    q_handler = inject_queue_handler(handlers_cfg, loggers_cfg, log)
    return cfg, q_handler
