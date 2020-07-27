import typing

try:
    from typing import Final
except ImportError:
    Final = str

WARNINGS: Final = 'HABApp.Warnings'
ERRORS: Final = 'HABApp.Errors'
INFOS: Final = 'HABApp.Infos'

RULES: Final = 'HABApp.Rules'
PARAM: Final = 'HABApp.Parameters'

ALL: typing.List[str] = [
    WARNINGS, ERRORS, INFOS,

    RULES, PARAM,
]
