import logging
import logging.config
from pathlib import Path
from typing import List

import pydantic

import HABApp
import eascheduler
from HABApp import __version__
from HABApp.config.config import CONFIG
from HABApp.config.logging import HABAppQueueHandler
from .errors import InvalidConfigError, AbsolutePathExpected
from .logging import create_default_logfile, get_logging_dict, rotate_files, inject_log_buffer
from .logging.buffered_logger import BufferedLogger

log = logging.getLogger('HABApp.Config')


def load_config(config_folder: Path):

    CONFIG.set_file_path(config_folder / 'config.yml')

    logging_cfg_path = config_folder / 'logging.yml'
    create_default_logfile(logging_cfg_path)

    loaded_logging = False

    # Try load the logging config
    try:
        load_logging_cfg(logging_cfg_path)
        loaded_logging = True
    except (AbsolutePathExpected, InvalidConfigError):
        pass

    load_habapp_cfg(do_print=not loaded_logging)

    if not loaded_logging:
        load_logging_cfg(logging_cfg_path)

    # Watch folders, so we can reload the config on the fly
    filter = HABApp.core.files.watcher.FileEndingFilter('.yml')
    watcher = HABApp.core.files.watcher.AggregatingAsyncEventHandler(
        config_folder, config_files_changed, filter, watch_subfolders=False
    )
    HABApp.core.files.watcher.add_folder_watch(watcher)

    HABApp.runtime.shutdown.register_func(stop_queue_handlers, last=True, msg='Stopping logging threads')
    CONFIG.habapp.logging.subscribe_for_changes(set_flush_delay)


def set_flush_delay():
    HABAppQueueHandler.FLUSH_DELAY = CONFIG.habapp.logging.flush_every


async def config_files_changed(paths: List[Path]):
    for path in paths:
        if path.name == 'config.yml':
            load_habapp_cfg()
        if path.name == 'logging.yml':
            load_logging_cfg(path)


def load_habapp_cfg(do_print=False):
    try:
        CONFIG.load_config_file()
    except pydantic.ValidationError as e:
        for line in str(e).splitlines():
            if do_print:
                print(line)
            else:
                log.error(line)
        raise InvalidConfigError from None

    # check if folders exist and print warnings, maybe because of missing permissions
    if not CONFIG.directories.rules.is_dir():
        log.warning(f'Folder for rules files does not exist: {CONFIG.directories.rules}')

    CONFIG.directories.create_folders()

    log.debug(f'Local Timezone: {eascheduler.const.local_tz}')
    location = CONFIG.location
    eascheduler.set_location(location.latitude, location.longitude, location.elevation)

    log.debug('Loaded HABApp config')


QUEUE_HANDLER: List['HABAppQueueHandler'] = []


def stop_queue_handlers():
    for qh in QUEUE_HANDLER:
        qh.signal_stop()
    while QUEUE_HANDLER:
        qh = QUEUE_HANDLER.pop()
        qh.stop()


def load_logging_cfg(path: Path):
    # stop buffered handlers
    stop_queue_handlers()

    buf_log = BufferedLogger()
    cfg = get_logging_dict(path, buf_log)

    if CONFIG.habapp.logging.use_buffer:
        q_handlers = inject_log_buffer(cfg, buf_log)
    else:
        q_handlers = []

    # load prepared logging
    try:
        logging.config.dictConfig(cfg)
    except Exception as e:
        print(f'Error loading logging config: {e}')
        log.error(f'Error loading logging config: {e}')
        raise InvalidConfigError from None

    rotate_files()

    # start buffered handlers
    for qh in q_handlers:
        QUEUE_HANDLER.append(qh)
        qh.start()

    logging.getLogger('HABApp').info(f'HABApp Version {__version__}')

    # write buffered messages
    buf_log.flush(log)
    return None
