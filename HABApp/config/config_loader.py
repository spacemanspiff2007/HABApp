import logging
import logging.config
import time
import traceback
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Dict, List

import ruamel.yaml

import HABApp
from HABApp import __version__
from . import CONFIG
from .default_logfile import get_default_logfile

_yaml_param = ruamel.yaml.YAML(typ='safe')
_yaml_param.default_flow_style = False
_yaml_param.default_style = False   # type: ignore
_yaml_param.width = 1000000         # type: ignore
_yaml_param.allow_unicode = True
_yaml_param.sort_base_mapping_type_on_output = False    # type: ignore


log = logging.getLogger('HABApp.Config')


class AbsolutePathExpected(Exception):
    pass


class InvalidConfigException(Exception):
    pass


class HABAppConfigLoader:

    def __init__(self, config_folder: Path):

        assert isinstance(config_folder, Path)
        assert config_folder.is_dir(), config_folder
        self.folder_conf = config_folder
        self.file_conf_habapp  = self.folder_conf / 'config.yml'
        self.file_conf_logging = self.folder_conf / 'logging.yml'

        # if the config does not exist it will be created
        self.__check_create_logging()

        # Load Config initially
        self.first_start = True
        try:
            self.load_cfg()
            load_cfg = False
        except Exception:
            load_cfg = True

        # Load logging configuration.
        try:
            self.load_log()
        except AbsolutePathExpected:
            # This error only occurs when the config was not loaded because of an exception.
            # Since we crash in load_cfg again we'll show that error because it's the root cause.
            pass

        # If there was an error reload the config again so we hopefully can log the error message
        if load_cfg:
            self.load_cfg()

        self.first_start = False

        # Watch folders so we can reload the config on the fly
        watcher = HABApp.core.files.watcher.AggregatingAsyncEventHandler(
            self.folder_conf, self.files_changed, file_ending='.yml', watch_subfolders=False
        )
        HABApp.core.files.watcher.add_folder_watch(watcher)

    def files_changed(self, paths: List[Path]):
        for path in paths:
            if path.name == 'config.yml':
                self.load_cfg()
            if path.name == 'logging.yml':
                self.load_log()

    def __check_create_logging(self):
        if self.file_conf_logging.is_file():
            return None

        print(f'Creating {self.file_conf_logging.name} in {self.file_conf_logging.parent}')
        with self.file_conf_logging.open('w', encoding='utf-8') as file:
            file.write(get_default_logfile())

        time.sleep(0.1)
        return None

    def load_cfg(self):

        CONFIG.load(self.file_conf_habapp)

        # check if folders exist and print warnings, maybe because of missing permissions
        if not CONFIG.directories.rules.is_dir():
            log.warning(f'Folder for rules files does not exist: {CONFIG.directories.rules}')

        log.debug('Loaded HABApp config')
        return None

    def load_log(self):
        # config gets created on startup - if it gets deleted we do nothing here
        if not self.file_conf_logging.is_file():
            return None

        with self.file_conf_logging.open('r', encoding='utf-8') as file:
            cfg = _yaml_param.load(file)    # type: Dict[str, Any]

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
                if not isinstance(CONFIG.directories.logging, Path):
                    raise AbsolutePathExpected()

                # Use defined parent folder
                p = (CONFIG.directories.logging / p).resolve()
                handler_cfg['filename'] = str(p)

        # make file version optional for config file
        log_version_info = True  # todo: remove this 06.2021
        if 'version' not in cfg:
            cfg['version'] = 1
            log_version_info = False

        # Allow the user to set his own logging levels (with aliases)
        for level, alias in cfg.pop('levels', {}).items():
            if not isinstance(level, int):
                level = logging._nameToLevel[level]
            logging.addLevelName(level, str(alias))

        # load prepared logging
        try:
            logging.config.dictConfig(cfg)
        except Exception as e:
            print(f'Error loading logging config: {e}')
            log.error(f'Error loading logging config: {e}')
            return None

        # Try rotating the logs on first start
        if self.first_start:
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
                    handler.close()
                    handler.doRollover()
                except Exception:
                    lines = traceback.format_exc().splitlines()
                    # cut away AbsolutePathExpected Exception from log output
                    start = 0
                    for i, line in enumerate(lines):
                        if line.startswith('Traceback'):
                            start = i
                    for line in lines[start:]:
                        log.error(line)
                finally:
                    handler.release()

        logging.getLogger('HABApp').info(f'HABApp Version {__version__}')

        if log_version_info:
            log.info('Entry "version" is no longer required in the logging configuration file')
        return None
