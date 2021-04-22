from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    import HABApp

FILES: Dict[str, 'HABApp.core.files.file.HABAppFile'] = {}


def file_state_changed(file: 'HABApp.core.files.file.HABAppFile'):
    for f in FILES.values():
        if f is not file:
            f.file_changed(file)
