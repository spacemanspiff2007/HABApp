from typing import Final


TOPIC_INFOS: Final    = 'HABApp.Infos'
TOPIC_WARNINGS: Final = 'HABApp.Warnings'
TOPIC_ERRORS: Final   = 'HABApp.Errors'

TOPIC_FILES: Final = 'HABApp.Files'
TOPIC_CONNECTIONS: Final = 'HABApp.Connections'


ALL_TOPICS: tuple[str, ...] = (
    TOPIC_INFOS, TOPIC_WARNINGS, TOPIC_ERRORS,

    TOPIC_FILES,
    TOPIC_CONNECTIONS
)
