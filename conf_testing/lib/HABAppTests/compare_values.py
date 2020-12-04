from .utils import get_bytes_text


def get_equal_text(value1, value2):

    return f'{get_bytes_text(value1)} ({str(type(value1))[8:-2]}) ' \
           f'{"==" if value1 == value2 else "!="} ' \
           f'{get_bytes_text(value2)} ({str(type(value2))[8:-2]})'
