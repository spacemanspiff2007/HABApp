from __future__ import annotations

from typing import TYPE_CHECKING

from HABApp.core.provider.type_helper import get_obj_parameters


if TYPE_CHECKING:
    from tests.test_core.test_provider.test_type_helper import ClsOuter


def func(obj: ClsOuter) -> int:
    return 1


def test_resolve() -> None:
    annotation = get_obj_parameters(func)

    from .test_type_helper import ClsOuter  # noqa: PLC0415
    assert len(annotation) == 1
    assert annotation['obj'] is ClsOuter
