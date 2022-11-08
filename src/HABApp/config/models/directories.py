import logging
import sys
from pathlib import Path
from typing import Optional

from easyconfig import BaseModel
from pydantic import Field, validator

from HABApp.config.platform_defaults import get_log_folder

log = logging.getLogger('HABApp.Config')


class DirectoriesConfig(BaseModel):
    """Configuration of directories that are used"""

    logging: Path = Field(get_log_folder(Path('log')), description='Folder where the logs will be written to')
    rules: Path = Field(Path('rules'), description='Folder from which the rule files will be loaded')

    # Optional Folders
    param: Optional[Path] = Field(Path('params'), description='Folder from which the parameter files will be loaded')
    config: Optional[Path] = Field(Path('config'), description='Folder from which configuration files '
                                                               '(e.g. for textual thing configuration) will be loaded')
    lib: Optional[Path] = Field(Path('lib'), description='Folder where additional libraries can be placed')

    @validator('*')
    def ensure_folder(cls, value: Optional[Path]):
        import HABApp.__cmd_args__

        if value is None:
            return value

        # only resolve if we have a path set
        if not value.is_absolute() and HABApp.__cmd_args__.CONFIG_FILE.name:
            value = HABApp.__cmd_args__.CONFIG_FILE.parent / value
            value = value.resolve()

        if value == HABApp.__cmd_args__.CONFIG_FILE:
            raise ValueError(
                f'Can not be the same as the path for the HABApp config! ({HABApp.__cmd_args__.CONFIG_FILE})'
            )

        return value

    def create_folders(self):

        # create folder structure if it does not exist
        if not self.rules.is_dir():
            self.rules.mkdir()
        if not self.logging.is_dir():
            self.logging.mkdir()

        if not self.param.is_dir():
            log.info(f'Parameters disabled! Folder {self.param} does not exist!')
            self.param = None

        if not self.config.is_dir():
            log.info(f'Manual thing configuration disabled! Folder {self.config} does not exist!')
            self.config = None

        # add path for user libraries
        if self.lib is not None and self.lib.is_dir():
            lib_path = str(self.lib)
            if lib_path not in sys.path:
                sys.path.insert(0, lib_path)
                log.debug(f'Added library folder "{lib_path}" to system path')
