from binascii import b2a_hex


def get_bytes_text(value: object) -> object:
    if isinstance(value, bytes) and len(value) > 300:
        return b2a_hex(value[:40]).decode() + ' ... ' + b2a_hex(value[-40:]).decode()
    return value


def get_equal_text(value1: object, value2: object) -> str:
    equal = value1 == value2 and isinstance(value1, value2.__class__)
    return f'{get_value_text(value1):s} {"==" if equal else "!="} {get_value_text(value2):s}'


def get_value_text(value: object) -> str:
    return f'{get_bytes_text(value)} ({str(type(value))[8:-2]})'
