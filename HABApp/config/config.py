import logging
import sys
from pathlib import Path

from EasyCo import ConfigFile, PathContainer

from ._conf_location import Location
from ._conf_mqtt import Mqtt
from ._conf_openhab import Openhab

log = logging.getLogger('HABApp.Config')


class Directories(PathContainer):
    logging: Path = Path('log')
    rules: Path = Path('rules')
    lib: Path = Path('lib')
    param: Path = Path('param')

    def on_all_values_set(self):
        try:
            # create folder structure if it does not exist
            if not self.rules.is_dir():
                self.rules.mkdir()
            if not self.logging.is_dir():
                self.logging.mkdir()

            # add path for libraries
            if self.lib.is_dir():
                lib_path = str(self.lib)
                if lib_path not in sys.path:
                    sys.path.insert(0, lib_path)
                    log.debug(f'Added library folder "{lib_path}" to path')
        except Exception as e:
            log.error(e)
            print(e)


class HABAppConfig(ConfigFile):
    location = Location()
    directories = Directories()
    mqtt = Mqtt()
    openhab = Openhab()


CONFIG: HABAppConfig = HABAppConfig()
