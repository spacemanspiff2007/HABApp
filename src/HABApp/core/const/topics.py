import typing

try:
    from typing import Final
except ImportError:
    Final = str


TOPIC_INFOS: Final = 'HABApp.Infos'
TOPIC_WARNINGS: Final = 'HABApp.Warnings'
TOPIC_ERRORS: Final = 'HABApp.Errors'

TOPIC_FILES: Final = 'HABApp.Files'


ALL_TOPICS: typing.List[str] = [
    TOPIC_WARNINGS, TOPIC_ERRORS, TOPIC_INFOS,

    TOPIC_FILES
]
