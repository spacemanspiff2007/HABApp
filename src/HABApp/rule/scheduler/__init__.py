from eascheduler import add_holiday, get_holiday_name, get_holidays_by_name, get_sun_position, is_holiday, pop_holiday
from eascheduler.builder import FilterBuilder as filter
from eascheduler.builder import TriggerBuilder as trigger
from whenever import hours, milliseconds, minutes, seconds

from HABApp.core.lib import InstantView

# Keep __all__ here: this module re-exports third-party symbols under public aliases (trigger/filter)
# so from HABApp.rule.scheduler import trigger remains valid and pyright/pylance don’t warn.
__all__ = [
    'trigger',
    'filter',
    'hours',
    'minutes',
    'seconds',
    'milliseconds',
    'add_holiday',
    'get_holiday_name',
    'get_holidays_by_name',
    'get_sun_position',
    'is_holiday',
    'pop_holiday',
    'InstantView',
]
