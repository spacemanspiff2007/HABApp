from pathlib import Path
from typing import Optional


def get_log_folder(default: Optional[Path] = None) -> Optional[Path]:
    # As a default we log into the openHAB folder
    choices = ('/var/log/openhab', '/opt/openhab/userdata/logs')
    for choice in choices:
        path = Path(choice)
        if path.is_dir():
            return path

    return default


def is_openhabian():
    return Path('/opt/openhabian').is_dir()
