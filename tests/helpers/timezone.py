from typing import Final

from whenever import PlainDateTime


def get_timezone_str(*, with_sign: bool = False) -> str:
    iso_str: Final = PlainDateTime(2023, 6, 17).assume_system_tz().format_iso()
    pos: Final = iso_str.find('[') - (6 if with_sign else 5)
    assert pos > 0
    return iso_str[pos:]


def remove_timezone_str(iso_str: str) -> str:
    pos: Final = iso_str.find('[') - 5
    assert pos > 0
    text: Final = iso_str[:pos]
    offset: Final = iso_str[pos:]
    assert offset[:2].isdigit(), offset
    assert offset[2] == ':', offset
    assert offset[3:5].isdigit(), offset
    return text
