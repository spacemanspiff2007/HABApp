from typing import Final, Tuple


TOPIC_INFOS: Final    = 'HABApp.Infos'
TOPIC_WARNINGS: Final = 'HABApp.Warnings'
TOPIC_ERRORS: Final   = 'HABApp.Errors'

TOPIC_FILES: Final = 'HABApp.Files'


ALL_TOPICS: Tuple[str, ...] = (
    TOPIC_INFOS, TOPIC_WARNINGS, TOPIC_ERRORS,

    TOPIC_FILES
)


TOPIC_EVENTS: Final = 'HABApp.EventBus'
