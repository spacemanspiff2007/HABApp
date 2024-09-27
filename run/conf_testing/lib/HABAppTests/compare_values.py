from .utils import get_bytes_text


def get_equal_text(value1, value2) -> str:
    return f'{get_value_text(value1)} {"==" if value1 == value2 else "!="} {get_value_text(value2)}'


def get_value_text(value) -> str:
    return f'{get_bytes_text(value)} ({str(type(value))[8:-2]})'
