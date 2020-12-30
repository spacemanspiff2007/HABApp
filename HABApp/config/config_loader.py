import logging
import logging.config
import time
import traceback
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path

import ruamel.yaml

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
            # try load logging config first. If we use abs path we can log errors when loading config.yml
            self.on_file_event(self.file_conf_logging)
            self.on_file_event(self.file_conf_habapp)
        except AbsolutePathExpected:
            self.on_file_event(self.file_conf_habapp)
            self.on_file_event(self.file_conf_logging)
        self.first_start = False

    def on_file_event(self, path: Path):
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
            log.warning( f'Folder for rules files does not exist: {CONFIG.directories.rules}')

        log.debug('Loaded HABApp config')
        return None

    def load_log(self):
        # config gets created on startup - if it gets deleted we do nothing here
        if not self.file_conf_logging.is_file():
            return None

        with self.file_conf_logging.open('r', encoding='utf-8') as file:
            cfg = _yaml_param.load(file)

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

        # load prepared logging
        try:
            logging.config.dictConfig(cfg)
        except Exception as e:
            print(f'Error loading logging config: {e}')
            return None
        log.debug('Loaded logging config')

        # Try rotating the logs on first start
        if self.first_start:
            for handler in logging._handlerList:
                try:
                    handler = handler()  # weakref -> call it to get object
                    if isinstance(handler, (RotatingFileHandler, TimedRotatingFileHandler)):
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

        logging.getLogger('HABApp').info(f'HABApp Version {__version__}')

        if log_version_info:
            log.info('Entry "version" is no longer required in the logging configuration file')
        return None
