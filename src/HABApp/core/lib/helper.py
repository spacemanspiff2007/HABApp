from collections.abc import Callable


def get_obj_name(obj: Callable) -> str:
    # not all callables have a __name__ attribute, i.e. Mock, lambda
    if (name := getattr(obj, '__name__', None)) is None:
        return repr(obj)
    return name
