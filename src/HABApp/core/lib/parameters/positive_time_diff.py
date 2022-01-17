from datetime import timedelta
from typing import Union

TH_POSITIVE_TIME_DIFF = Union[int, float, timedelta]


def get_positive_time_diff(arg: TH_POSITIVE_TIME_DIFF, round_digits=None) -> Union[int, float]:
    if isinstance(arg, timedelta):
        diff = arg.total_seconds()
        if round_digits is not None:
            diff = round(diff, round_digits)
    elif isinstance(arg, float):
        diff = round(arg, round_digits) if round_digits is not None else arg
    elif isinstance(arg, int):
        diff = arg
    else:
        raise ValueError(f'Invalid type: {type(arg)}')

    if diff <= 0:
        raise ValueError(f'Time difference must be positive! ({arg})')
    return diff
