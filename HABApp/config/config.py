import logging
import sys
from pathlib import Path

from EasyCo import ConfigFile, PathContainer, ConfigEntry

from ._conf_location import Location
from ._conf_mqtt import Mqtt
from ._conf_openhab import Openhab

log = logging.getLogger('HABApp.Config')


class Directories(PathContainer):
    logging: Path = ConfigEntry(Path('log'), description='Folder where the logs will be written to')
    rules: Path = ConfigEntry(Path('rules'), description='Folder from which the rule files will be loaded')
    param: Path = ConfigEntry(Path('param'), description='Folder from which the parameter files will be loaded')
    config: Path = ConfigEntry(Path('config'), description='Folder from which configuration files will be loaded')
    lib: Path = ConfigEntry(Path('lib'), description='Folder where additional libraries can be placed')

    def on_all_values_set(self):
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


class HABAppConfig(ConfigFile):
    location = Location()
    directories = Directories()
    mqtt = Mqtt()
    openhab = Openhab()


CONFIG: HABAppConfig = HABAppConfig()
