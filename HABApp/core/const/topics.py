import typing

try:
    from typing import Final
except ImportError:
    Final = str


INFOS: Final = 'HABApp.Infos'
WARNINGS: Final = 'HABApp.Warnings'
ERRORS: Final = 'HABApp.Errors'

FILES: Final = 'HABApp.Files'


ALL: typing.List[str] = [
    WARNINGS, ERRORS, INFOS,

    FILES
]
