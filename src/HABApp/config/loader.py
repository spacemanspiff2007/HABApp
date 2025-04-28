import logging
import logging.config
from pathlib import Path

import eascheduler
import pydantic

from HABApp import __version__
from HABApp.config.config import CONFIG
from HABApp.config.logging import HABAppQueueHandler, load_logging_file
from HABApp.core import shutdown
from HABApp.core.internals.proxy.proxies import uses_file_manager

from .debug import setup_debug
from .errors import AbsolutePathExpected, InvalidConfigError
from .logging import create_default_logfile, get_logging_dict
from .logging.buffered_logger import BufferedLogger


log = logging.getLogger('HABApp.Config')


file_manager = uses_file_manager()


def setup_habapp_configuration(config_folder: Path) -> None:

    CONFIG.set_file_path(config_folder / 'config.yml')
    preprocess = CONFIG.load_preprocess
    preprocess.set_log_func(log.warning)
    # old sse event handler config, remove 2026
    preprocess.delete_entry(('openhab', 'connection', 'buffer'))
    preprocess.delete_entry(('openhab', 'connection', 'topic filter'))
    # change name for param folder, remove 2026
    preprocess.move_entry(('directories', 'param'), ('directories', 'params'))

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

    shutdown.register(stop_queue_handlers, msg='Stop logging queue handlers', last=True)

    setup_debug()

    watcher = file_manager.get_file_watcher()
    watcher.watch_file('config.log_file', config_file_changed, config_folder / 'logging.yml', habapp_internal=True)
    watcher.watch_file('config.cfg_file', config_file_changed, config_folder / 'config.yml', habapp_internal=True)

    CONFIG.habapp.logging.subscribe_for_changes(set_flush_delay)


def set_flush_delay() -> None:
    HABAppQueueHandler.FLUSH_DELAY = CONFIG.habapp.logging.flush_every


async def config_file_changed(path: str) -> None:
    file = Path(path)
    if file.name == 'config.yml':
        load_habapp_cfg()
    if file.name == 'logging.yml':
        load_logging_cfg(file)


def load_habapp_cfg(do_print=False) -> None:
    def error(text: str) -> None:
        if do_print:
            print(text)
        else:
            log.error(text)

    try:
        CONFIG.load_config_file()
    except pydantic.ValidationError as e:
        for line in str(e).splitlines():
            error(line)
        raise InvalidConfigError from None

    # check if folders exist and print warnings, maybe because of missing permissions
    if not CONFIG.directories.rules.is_dir():
        log.warning(f'Folder for rules files does not exist: {CONFIG.directories.rules}')

    CONFIG.directories.create_folders()

    location = CONFIG.location
    eascheduler.set_location(location.latitude, location.longitude, location.elevation)

    if not location.country:
        log.warning('No country is set in the config file. Holidays will not be available.')
    else:
        try:
            eascheduler.setup_holidays(location.country, location.subdivision if location.subdivision else None)
        except Exception as e:
            for line in str(e).splitlines():
                error(line)

    log.debug('Loaded HABApp config')


QUEUE_HANDLER: list['HABAppQueueHandler'] = []


def stop_queue_handlers() -> None:
    for qh in QUEUE_HANDLER:
        qh.signal_stop()
    while QUEUE_HANDLER:
        qh = QUEUE_HANDLER.pop()
        qh.stop()


def load_logging_cfg(path: Path) -> None:
    # If the logging file gets accidentally deleted we do nothing
    if (logging_yaml := load_logging_file(path)) is None:
        return None

    # stop buffered handlers
    stop_queue_handlers()

    buf_log = BufferedLogger()
    cfg, q_handlers = get_logging_dict(logging_yaml, buf_log)

    # load prepared logging
    try:
        logging.config.dictConfig(cfg)
    except Exception as e:
        print(f'Error loading logging config: {e}')
        log.error(f'Error loading logging config: {e}')
        raise InvalidConfigError from None

    # start buffered handlers
    for qh in q_handlers:
        QUEUE_HANDLER.append(qh)
        qh.start()

    logging.getLogger('HABApp').info(f'HABApp Version {__version__}')

    # write buffered messages
    buf_log.flush(log)
    return None
