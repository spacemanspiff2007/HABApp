import logging
import sys
from pathlib import Path

from easyconfig import PathModel
from pydantic import Field

from HABApp.config.platform_defaults import get_log_folder

log = logging.getLogger('HABApp.Config')


class DirectoriesConfig(PathModel):
    logging: Path = Field(get_log_folder(Path('log')), description='Folder where the logs will be written to')
    rules: Path = Field(Path('rules'), description='Folder from which the rule files will be loaded')
    param: Path = Field(Path('params'), description='Folder from which the parameter files will be loaded')
    config: Path = Field(Path('config'), description='Folder from which configuration files '
                                                     '(e.g. for textual thing configuration) will be loaded')
    lib: Path = Field(Path('lib'), description='Folder where additional libraries can be placed')

    def on_all_values_set(self):

        # Configuration folder of HABApp can not be one of the configured folders
        for name, path in {attr: getattr(self, attr) for attr in ('rules', 'param', 'config')}.items():
            if path == self._easyconfig.base_path:
                msg = f'Path for {name} can not be the same as the path for the HABApp config! ({path})'
                log.error(msg)
                sys.exit(msg)

        try:
            # create folder structure if it does not exist
            if not self.rules.is_dir():
                self.rules.mkdir()
            if not self.logging.is_dir():
                self.logging.mkdir()
            if not self.config.is_dir():
                log.info(f'Manual thing configuration disabled! Folder {self.config} does not exist!')

            # add path for libraries
            if self.lib.is_dir():
                lib_path = str(self.lib)
                if lib_path not in sys.path:
                    sys.path.insert(0, lib_path)
                    log.debug(f'Added library folder "{lib_path}" to system path')
        except Exception as e:
            log.error(e)
            print(e)
