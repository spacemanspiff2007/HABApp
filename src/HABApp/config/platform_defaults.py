from pathlib import Path


def get_log_folder(default: Path | None = None) -> Path:
    # As a default we log into the openHAB folder
    choices = ('/var/log/openhab', '/opt/openhab/userdata/logs')
    for choice in choices:
        path = Path(choice)
        if path.is_dir():
            return path

    if default is None:
        raise ValueError('No log folder found and no default provided!')

    return default


def is_openhabian() -> bool:
    return Path('/opt/openhabian').is_dir()
