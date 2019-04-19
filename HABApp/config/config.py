import codecs
import logging
import logging.config
import time
from pathlib import Path
import sys

import ruamel.yaml
from voluptuous import MultipleInvalid, Schema

from HABApp.__version__ import __VERSION__
from ._conf_mqtt import Mqtt
from ._conf_openhab import Openhab
from .configentry import ConfigEntry
from .default_logfile import get_default_logfile

from HABApp.runtime import FileEventTarget

_yaml_param = ruamel.yaml.YAML(typ='safe')
_yaml_param.default_flow_style = False
_yaml_param.default_style = False
_yaml_param.width = 1000000
_yaml_param.allow_unicode = True
_yaml_param.sort_base_mapping_type_on_output = False


log = logging.getLogger('HABApp.Config')


class Directories(ConfigEntry):
    def __init__(self):
        super().__init__()
        self.logging: Path = 'log'
        self.rules: Path   = 'rules'
        self.lib: Path     = 'lib'
        self.param: Path   = 'param'


class Config(FileEventTarget):

    def __init__(self, runtime, config_folder : Path):

        import HABApp.runtime
        assert isinstance(runtime, HABApp.runtime.Runtime)
        self.__runtime = runtime

        assert isinstance(config_folder, Path)
        assert config_folder.is_dir(), config_folder
        self.folder_conf = config_folder
        self.file_conf_habapp  = self.folder_conf / 'config.yml'
        self.file_conf_logging = self.folder_conf / 'logging.yml'

        # these are the accessible config entries
        self.directories = Directories()
        self.mqtt = Mqtt()
        self.openhab = Openhab()

        # if the config does not exist it will be created
        self.__check_create_config()
        self.__check_create_logging()

        # folder watcher
        self.__runtime.folder_watcher.watch_folder(
            folder=self.folder_conf,
            file_ending='.yml',
            event_target=self
        )

        # Load Config initially
        self.first_start = True
        self.add_file(self.file_conf_habapp)
        self.add_file(self.file_conf_logging)
        self.first_start = False

    def add_file(self, path: Path):
        self.reload_file(path)

    def reload_file(self, path: Path):
        if path.name == 'config.yml':
            self.load_cfg()
        if path.name == 'logging.yml':
            self.load_log()

    def remove_file(self, path: Path):
        pass

    def __check_create_config(self):
        if self.file_conf_habapp.is_file():
            return None

        cfg = {}
        self.directories.insert_data(cfg)
        self.openhab.insert_data(cfg)
        self.mqtt.insert_data(cfg)

        print( f'Creating {self.file_conf_habapp.name} in {self.file_conf_habapp.parent}')
        with self.file_conf_habapp.open('w', encoding='utf-8') as file:
            _yaml_param.dump(cfg, file)

        # Create default folder for rules, too
        # Logging directories will get created elsewhere
        # Param files are optional
        self.directories.rules.mkdir()

        time.sleep(0.1)
        return None


    def __check_create_logging(self):
        if self.file_conf_logging.is_file():
            return None

        print(f'Creating {self.file_conf_logging.name} in {self.file_conf_logging.parent}')
        with self.file_conf_logging.open('w', encoding='utf-8') as file:
            file.write(get_default_logfile())

        time.sleep(0.1)
        return None

    def load_cfg(self):
        # File has to exist - check because we also get FileDelete events
        if not self.file_conf_habapp.is_file():
            return

        with self.file_conf_habapp.open('r', encoding='utf-8') as file:
            cfg = _yaml_param.load(file)
        try:
            _s = {}
            self.directories.update_schema(_s)
            self.openhab.update_schema(_s)
            self.mqtt.update_schema(_s)
            cfg = Schema(_s)(cfg)
        except MultipleInvalid as e:
            log.error( f'Error loading config:')
            log.error( e)
            return

        self.directories.load_data(cfg)
        self.openhab.load_data(cfg)
        self.mqtt.load_data(cfg)

        # make Path absolute for all directory entries
        for k, v in self.directories.iter_entry():
            __entry  = Path(v)
            if not __entry.is_absolute():
                __entry = self.folder_conf / __entry
                self.directories.__dict__[k] = __entry.resolve()

        if not self.directories.logging.is_dir():
            print( f'Creating log-dir: {self.directories.logging}')
            self.directories.logging.mkdir()

        log.debug('Loaded HABApp config')

        # Set path for libraries
        if self.directories.lib.is_dir():
            lib_path = str(self.directories.lib)
            if lib_path not in sys.path:
                sys.path.insert(0, lib_path)
                log.debug( f'Added library folder "{lib_path}" to path')

        # check if folders exist and print warnings
        if not self.directories.rules.is_dir():
            log.warning( f'Folder for rules files does not exist: {self.directories.rules}')


    def load_log(self):
        # File has to exist - check because we also get FileDelete events
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
                p = (self.directories.logging / p).resolve()
                handler_cfg['filename'] = str(p)

            # Delete old Log-Files on startup
            if self.first_start and p.is_file():
                try:
                    # default is utf-8 logging so we write BOM
                    with open(p, mode='wb') as f:
                        f.write(codecs.BOM_UTF8)
                finally:
                    pass

        # load prepared logging
        logging.config.dictConfig(cfg)
        log.debug('Loaded logging config')

        logging.getLogger('HABApp').info(f'HABApp Version {__VERSION__}')
