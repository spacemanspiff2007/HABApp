try:
    from typing import Final
except ImportError:
    Final = str

WARNINGS: Final = 'HABApp.Warnings'
ERRORS: Final = 'HABApp.Errors'

RULES: Final = 'HABApp.Rules'
PARAM: Final = 'HABApp.Parameters'
