import logging
import logging.config
from pathlib import Path
from typing import Final

import eascheduler
import pydantic

from HABApp import __version__
from HABApp.config.config import CONFIG
from HABApp.config.logging import HABAppQueueHandler, LogQueueManager, load_logging_file
from HABApp.core.files import FileManager
from HABApp.core.provider import HABAPP_PROVIDER

from .errors import AbsolutePathExpected, InvalidConfigError
from .logging import create_default_logfile, get_logging_dict
from .logging.buffered_logger import BufferedLogger


log = logging.getLogger('HABApp.Config')


async def setup_habapp_configuration(config_folder: Path) -> None:
    logging_cfg_path: Final = config_folder / 'logging.yml'
    habapp_cfg_path: Final = config_folder / 'config.yml'

    CONFIG.set_file_path(habapp_cfg_path)
    preprocess = CONFIG.load_preprocess
    preprocess.set_log_func(log.warning)
    # old sse event handler config, remove 2026
    preprocess.delete_entry(('openhab', 'connection', 'buffer'))
    preprocess.delete_entry(('openhab', 'connection', 'topic filter'))
    # change name for param folder, remove 2026
    preprocess.move_entry(('directories', 'param'), ('directories', 'params'))

    # debug settings, remove 2027
    preprocess.move_entry(('habapp', 'debug', 'periodic traceback'), ('habapp', 'debug', 'dump threads'))
    preprocess.rename_entry(('habapp', 'debug', 'traceback on shutdown signal'), 'dump threads on shutdown signal')

    create_default_logfile(logging_cfg_path)

    loaded_logging = False

    # Try load the logging config
    try:
        await load_logging_cfg(logging_cfg_path)
        loaded_logging = True
    except (AbsolutePathExpected, InvalidConfigError):
        pass

    await load_habapp_cfg(do_print=not loaded_logging)

    if not loaded_logging:
        await load_logging_cfg(logging_cfg_path)

    file_manager = await HABAPP_PROVIDER.get(FileManager)

    watcher = file_manager.get_file_watcher()
    watcher.watch_file('config.log_file', config_file_changed, logging_cfg_path, habapp_internal=True)
    watcher.watch_file('config.cfg_file', config_file_changed, habapp_cfg_path, habapp_internal=True)

    CONFIG.habapp.logging.subscribe_for_changes(set_flush_delay)


def set_flush_delay() -> None:
    HABAppQueueHandler.FLUSH_DELAY = CONFIG.habapp.logging.flush_every


async def config_file_changed(path: str) -> None:
    file = Path(path)
    if file.name == 'config.yml':
        await load_habapp_cfg()
    if file.name == 'logging.yml':
        await load_logging_cfg(file)


async def load_habapp_cfg(do_print: bool = False) -> None:
    def error(text: str) -> None:
        if do_print:
            print(text)
        else:
            log.error(text)

    try:
        await CONFIG.load_config_file()
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
            eascheduler.setup_holidays(location.country, location.subdivision or None)
        except Exception as e:
            for line in str(e).splitlines():
                error(line)

    log.debug('Loaded HABApp config')


async def load_logging_cfg(path: Path) -> None:
    # If the logging file gets accidentally deleted we do nothing
    if (logging_yaml := load_logging_file(path)) is None:
        return None

    manager = await HABAPP_PROVIDER.get(LogQueueManager)
    manager.stop()

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
    manager.add(q_handlers)

    logging.getLogger('HABApp').info(f'HABApp Version {__version__}')

    # write buffered messages
    buf_log.flush(log)
    return None
