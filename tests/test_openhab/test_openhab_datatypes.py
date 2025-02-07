from datetime import datetime

import pytest
from whenever import SystemDateTime

from HABApp.openhab.items import DatetimeItem, NumberItem


@pytest.mark.parametrize('value, target', (('0', 0), ('-15', -15), ('55', 55), ))
def test_type_number(value: str, target: int) -> None:
    ret = NumberItem._state_from_oh_str(value)
    assert ret == target
    assert isinstance(ret, int)


@pytest.mark.parametrize(
    'value, target', (('0.0', 0), ('-99.99', -99.99), ('99.99', 99.99), ('0', 0), ('-15', -15), ('55', 55), )
)
def test_type_decimal(value: str, target: int) -> None:
    ret = NumberItem._state_from_oh_str(value)
    assert ret == target
    assert type(ret) is target.__class__


def __get_dt_parms():
    # We have to build the offset str dynamically otherwise we will fail during CI because it's in another timezone
    offset_str = SystemDateTime(2023, 6, 17).format_common_iso()[-5:].replace(':', '')

    return (
        pytest.param(f'2023-06-17T15:31:04.754673068+{offset_str}', datetime(2023, 6, 17, 15, 31, 4, 754673), id='T1'),
        pytest.param(f'2023-06-17T15:31:04.754673+{offset_str}', datetime(2023, 6, 17, 15, 31, 4, 754673), id='T2'),
        pytest.param(f'2023-06-17T15:31:04.754+{offset_str}', datetime(2023, 6, 17, 15, 31, 4, 754000), id='T3'),
    )


@pytest.mark.parametrize(('value', 'target'), __get_dt_parms())
def test_type_datetime(value: str, target: datetime) -> None:
    assert DatetimeItem._state_from_oh_str(value) == target
