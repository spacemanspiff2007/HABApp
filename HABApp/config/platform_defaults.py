from pathlib import Path
from typing import Optional


def get_log_folder(default: Optional[Path] = None) -> Optional[Path]:
    # As a default we log into the openhab folder
    choices = ('/var/log/openhab', '/opt/openhab/userdata/logs')
    for choice in choices:
        path = Path(choice)
        if path.is_dir():
            return path

    return default
