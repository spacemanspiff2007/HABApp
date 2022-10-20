import inspect
from typing import Iterable, Optional

from tests.helpers.inspect.module import get_module_classes


def check_class_annotations(module_name: str, exclude: Optional[Iterable[str]] = None):
    """Ensure that the annotations match with the actual variables"""

    classes = get_module_classes(module_name, exclude=exclude)
    for name, cls in classes.items():
        c = cls()
        args = dict(filter(
            lambda x: not x[0].startswith('__'),
            dict(inspect.getmembers(c, lambda x: not inspect.ismethod(x))).items())
        )

        # Check that all vars are in __annotations__
        for arg_name in args:
            assert arg_name in c.__annotations__, f'"{arg_name}" is missing in annotations!"\n' \
                                                  f'members    : {", ".join(sorted(args))}\n' \
                                                  f'annotations: {", ".join(sorted(c.__annotations__))}'

        for arg_name in c.__annotations__:
            assert arg_name in args, f'"{arg_name}" is missing in args!"\n' \
                                     f'members    : {", ".join(sorted(args))}\n' \
                                     f'annotations: {", ".join(sorted(c.__annotations__))}'
