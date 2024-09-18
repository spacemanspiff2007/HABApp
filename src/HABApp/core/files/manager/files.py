from typing import TYPE_CHECKING


if TYPE_CHECKING:
    import HABApp

FILES: dict[str, 'HABApp.core.files.file.HABAppFile'] = {}


def file_state_changed(file: 'HABApp.core.files.file.HABAppFile') -> None:
    for f in FILES.values():
        if f is not file:
            f.file_changed(file)
