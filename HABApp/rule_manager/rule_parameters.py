import logging
import threading
import traceback
import typing
from pathlib import Path

import ruamel.yaml

import HABApp
from HABApp.runtime import FileEventTarget
from HABApp.util import PrintException

log = logging.getLogger('HABApp.RuleParameters')

_yml_setup = ruamel.yaml.YAML()
_yml_setup.default_flow_style = False
_yml_setup.default_style = False
_yml_setup.width = 1000000
_yml_setup.allow_unicode = True
_yml_setup.sort_base_mapping_type_on_output = False


class RuleParameters(FileEventTarget):
    UNITTEST = False

    @PrintException
    def __init__(self, config, folder_watcher):

        # serialize loading
        self.__lock = threading.Lock()

        self.params: typing.Dict[str, dict] = {}

        if RuleParameters.UNITTEST:
            return
        assert isinstance(config, HABApp.config.Config)
        assert isinstance(folder_watcher, HABApp.runtime.folder_watcher.FolderWatcher)
        self.config = config

        if not self.config.directories.param.is_dir():
            log.info(f'Parameter files disabled. Folder {self.config.directories.param} does not exist!')
            return

        # folder watcher
        folder_watcher.watch_folder(
            folder=self.config.directories.param,
            file_ending='.yml',
            event_target=self,
            worker_factory=lambda x : HABApp.core.WrappedFunction(x, logger=log).run,
            watch_subfolders=False
        )

        # load all parameter files
        def load_all_files():
            for f in self.config.directories.param.glob('**/*.yml'):
                try:
                    self.add_file(f)
                except Exception as e:
                    log.error(e)
        HABApp.core.WrappedFunction(load_all_files, logger=log, name='Load all parameter files').run()

    def reload_file(self, path: Path):
        self.add_file(path)

    def remove_file(self, path: Path):
        try:
            with self.__lock:
                self.params.pop(path.stem)
        except Exception:
            log.error(f"Could not remove parameters from {path.name}!")
            for l in traceback.format_exc().splitlines():
                log.error(l)
            return None

        log.debug(f'Removed params from {path.name}!')

    def add_file(self, path: Path):
        try:
            with self.__lock:
                with path.open( mode='r', encoding='utf-8') as file:
                    data = _yml_setup.load(file)
                if data is None:
                    data = {}
                self.params[path.stem] = data
        except Exception:
            log.error(f"Could not load params from {path.name}!")
            for l in traceback.format_exc().splitlines():
                log.error(l)
            return None

        log.debug(f'Loaded params from {path.name}!')

    def save_file(self, file: str):
        assert isinstance(file, str), type(file)

        if RuleParameters.UNITTEST:
            return None

        filename = self.config.directories.param / (file + '.yml')
        with self.__lock:
            log.info(f'Updated {filename}')
            with filename.open('w', encoding='utf-8') as file:
                _yml_setup.dump(self.params[file], file)

    def add_param(self, file, *keys, default_value):
        save = False

        if file not in self.params:
            save = True
            self.params[file] = param = {}
        else:
            param = self.params[file]

        if keys:
            # Create structure
            for key in keys[:-1]:
                if key not in param:
                    param[key] = {}
                    save = True
                param = param[key]

            # Create value
            if keys[-1] not in param:
                param[keys[-1]] = default_value
                save = True

        if save:
            self.save_file(file)
        return None

    def get_param(self, file, *keys):
        try:
            param = self.params[file]
        except KeyError:
            raise FileNotFoundError(f'File {file}.yml not found in params folder!')

        # lookup parameter
        for key in keys:
            param = param[key]
        return param
