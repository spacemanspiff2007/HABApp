from builtins import max as _max
from builtins import min as _min


def max(*args, default=None):
    """Behaves like the built in max function but ignores any ``None`` values. e.g. ``max([1, None, 2]) == 2``.
    If the iterable is empty ``default`` will be returned.

    :param args: Single iterable or 1..n arguments
    :param default: Value that will be returned if the iterable is empty
    :return: max value
    """
    return _max(
        filter(lambda x: x is not None, args[0] if len(args) == 1 else args),
        default=default
    )


def min(*args, default=None):
    """Behaves like the built in min function but ignores any ``None`` values. e.g. ``min([1, None, 2]) == 1``.
    If the iterable is empty ``default`` will be returned.

    :param args: Single iterable or 1..n arguments
    :param default: Value that will be returned if the iterable is empty
    :return: min value
    """
    return _min(
        filter(lambda x: x is not None, args[0] if len(args) == 1 else args),
        default=default
    )
