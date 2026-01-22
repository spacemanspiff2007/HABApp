from collections.abc import AsyncGenerator, Generator
from typing import Annotated, Any

from HABApp.core.provider.type_helper import _get_types_from_hint, _resolve_origins, get_return_type


def test_types_from_hint() -> None:
    assert _get_types_from_hint('None') == ('None', )
    assert _get_types_from_hint('list[str]') == ('list', 'str')
    assert _get_types_from_hint('Generator[Any, Any, Any]') == ('Generator', 'Any')
    assert _get_types_from_hint('A | B') == ('A', 'B')
    assert _get_types_from_hint('dict[A | B] | C') == ('dict', 'A', 'B', 'C')


def test_resolve_origins() -> None:
    assert _resolve_origins(Generator[dict, Any, Any]) is dict
    assert _resolve_origins(AsyncGenerator[dict, Any]) is dict
    assert _resolve_origins(Annotated[dict, Any]) is dict

    assert _resolve_origins(dict[str, str]) == dict[str, str]
    assert _resolve_origins(dict[Annotated[int, 'asdf'], str]) == dict[int, str]
    assert _resolve_origins(list[Annotated[int, 'asdf']]) == list[int]
    assert _resolve_origins(tuple[Annotated[int, 'asdf'], ...]) == tuple[int, ...]


def test_get_return_type_simple() -> None:
    class A:
        def a(self) -> str:
            pass

        @classmethod
        def b(self) -> Generator[int, None, None]:
            pass

        @staticmethod
        def c(self) -> bool:
            pass

    assert get_return_type(A.a) is str
    assert get_return_type(A.b) is int
    assert get_return_type(A.c) is bool

    class B:
        def a(self) -> 'str':
            pass

    assert get_return_type(B.a) is str


class ClsOuter:
    pass


class B:
    class ClsInner:
        pass

    @classmethod
    def outer_type(cls) -> ClsOuter:
        pass

    @classmethod
    def outer_str(cls) -> 'ClsOuter':
        pass

    @classmethod
    def inner_type(cls) -> ClsInner:
        pass

    @classmethod
    def inner_str(cls) -> 'ClsInner':
        pass


def test_get_return_type_class() -> None:
    assert get_return_type(B.outer_type) is ClsOuter
    assert get_return_type(B.outer_str) is ClsOuter
    assert get_return_type(B.inner_type) is B.ClsInner
    assert get_return_type(B.inner_str) is B.ClsInner
