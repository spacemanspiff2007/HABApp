import logging
import logging.config
import re
from pathlib import Path
from HABApp.util import SimpleFileWatcher, CallbackHelper

import ruamel.yaml
from voluptuous import Schema, Required, MultipleInvalid, Coerce, Invalid, Optional

from watchdog.observers import Observer


def TimeZoneValidator(msg=None):
    __re = re.compile('[+-]\d{4}')
    def f(v):
        v = str(v)
        if __re.match(v):
            return v
        else:
            raise Invalid(msg or ( f"incorrect timezone ({v})! Example: +1000 or -1030"))
    return f


valid_config = Schema({
    Required('ping') : {
        Required('enabled') : bool,
        Required('item'): str,
    },
    Required('directories') : {
        Required('logging') : str,
        Required('rules'): str,
    },
    Required('connection') :{
        Required('host'): str,
        Required('port'): Coerce(int),
        Required('user', default=''): str,
        Required('pass', default=''): str,
    },
    Required('timezone') : TimeZoneValidator(),
    Required('async timeout'): Coerce(int),
})

_yaml_param = ruamel.yaml.YAML(typ='safe')
_yaml_param.default_flow_style = False
_yaml_param.default_style = False
_yaml_param.width = 1000000
_yaml_param.allow_unicode = True
_yaml_param.sort_base_mapping_type_on_output = False


log = logging.getLogger('HABApp.Config')

class Config:

    def __init__(self, config_folder : Path= None, shutdown_helper : CallbackHelper = None):
        assert isinstance(config_folder, Path)
        assert config_folder.is_dir(), config_folder
        self.folder_conf = config_folder

        self.folder_log : Path = None

        self.ping_enabled = False
        self.ping_item    = ''

        self.directories = {}
        self.connection = {}
        self.timezone = None

        self.async_timeout : int

        self.config = {}

        self.__once = False

        # folder watcher
        self.__folder_watcher = Observer()
        self.__folder_watcher.schedule(SimpleFileWatcher(self.__file_changed, file_ending='.yml'), str(self.folder_conf))
        self.__folder_watcher.start()

        #proper shutdown
        shutdown_helper.register_func(self.__folder_watcher.stop)
        shutdown_helper.register_func(self.__folder_watcher.join, last=True)

        #Load Config initially
        self.__file_changed('ALL')

    def __file_changed(self, path):
        if path == 'ALL' or path.name == 'config.yml':
            self.load_cfg()
        if path == 'ALL' or path.name == 'logging.yml':
            self.load_log()
        return None



    def load_cfg(self):
        with open(self.folder_conf / 'config.yml', 'r', encoding='utf-8') as file:
            cfg = _yaml_param.load(file)
        try:
            cfg = valid_config(cfg)
        except MultipleInvalid as e:
            log.error( f'Error loading config:')
            log.error( e)
            return

        self.timezone = cfg['timezone']
        self.directories = cfg['directories']
        self.connection = cfg['connection']

        self.ping_enabled = cfg['ping']['enabled']
        self.ping_item    = cfg['ping']['item']
        self.config = cfg

        self.async_timeout = cfg['async timeout']

        # make abs Path for all directories
        for k, v in self.directories.items():
            __entry  = Path(v)
            if not __entry.is_absolute():
                __entry = self.folder_conf / __entry
                self.directories[k] = __entry.resolve()

        self.folder_log = Path(cfg['directories']['logging'])
        if not self.folder_log.is_dir():
            print( f'Creating log-dir: {self.folder_log}')
            self.folder_log.mkdir()

        log.debug('Loaded HABApp config')


    def load_log(self):
        if self.directories is None:
            return None

        with open(self.folder_conf / 'logging.yml', 'r', encoding='utf-8') as file:
            cfg = _yaml_param.load(file)

        # fix filenames
        for handler, handler_cfg in cfg.get('handlers', {}).items():
            if 'filename' not in handler_cfg:
                continue

            #make Filenames absolute path in the log folder if not specified
            p = Path(handler_cfg['filename'])
            if not p.is_absolute():
                p = (self.folder_log / p).resolve()
                handler_cfg['filename'] = str(p)

        #load prepared logging
        logging.config.dictConfig(cfg)
        log.debug('Loaded logging config')