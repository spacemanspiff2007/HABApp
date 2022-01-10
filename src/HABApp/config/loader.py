import logging
import logging.config
from pathlib import Path
from typing import List

import pydantic

import HABApp
from HABApp import __version__
from HABApp.config.config import CONFIG
from .errors import InvalidConfigError, AbsolutePathExpected
from .logging import create_default_logfile, get_logging_dict, rotate_files

log = logging.getLogger('HABApp.Config')


def load_config(config_folder: Path):

    CONFIG.set_file_path(config_folder / 'config.yml')

    logging_cfg_path = config_folder / 'logging.yml'
    create_default_logfile(logging_cfg_path)

    try:
        load_habapp_cfg()
        loaded_cfg = True
    except Exception:
        loaded_cfg = False

    try:
        load_logging_cfg(logging_cfg_path)
        rotate_files()
    except AbsolutePathExpected:
        # This error only occurs when the config was not loaded because of an exception.
        # Since we crash in load_cfg again we'll show that error because it's the root cause.
        pass

    # If there was an error reload the config again so we hopefully can log the error message
    if not loaded_cfg:
        load_habapp_cfg()

    # Watch folders so we can reload the config on the fly
    filter = HABApp.core.files.watcher.FileEndingFilter('.yml')
    watcher = HABApp.core.files.watcher.AggregatingAsyncEventHandler(
        config_folder, config_files_changed, filter, watch_subfolders=False
    )
    HABApp.core.files.watcher.add_folder_watch(watcher)


async def config_files_changed(self, paths: List[Path]):
    for path in paths:
        if path.name == 'config.yml':
            load_habapp_cfg()
        if path.name == 'logging.yml':
            self.load_log()


def load_habapp_cfg():
    try:
        CONFIG.load_file()
    except pydantic.ValidationError as e:
        for line in str(e).splitlines():
            log.error(line)
        raise InvalidConfigError from None

    # check if folders exist and print warnings, maybe because of missing permissions
    if not CONFIG.directories.rules.is_dir():
        log.warning(f'Folder for rules files does not exist: {CONFIG.directories.rules}')

    log.debug('Loaded HABApp config')


def load_logging_cfg(path: Path):
    log_msgs = []
    cfg = get_logging_dict(path, log_msgs)

    # load prepared logging
    try:
        logging.config.dictConfig(cfg)
    except Exception as e:
        print(f'Error loading logging config: {e}')
        log.error(f'Error loading logging config: {e}')
        return None

    logging.getLogger('HABApp').info(f'HABApp Version {__version__}')

    # log delayed messages
    for lvl, msg in log_msgs:
        log.log(lvl, msg)
    return None
