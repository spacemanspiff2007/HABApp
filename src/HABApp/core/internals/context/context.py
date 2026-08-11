from __future__ import annotations

from contextvars import ContextVar
from functools import wraps
from inspect import getmembers_static, iscoroutinefunction, isfunction
from typing import TYPE_CHECKING, Any, Final

from HABApp.core.errors import ContextBoundObjectIsAlreadyLinkedError, ContextBoundObjectIsAlreadyUnlinkedError


if TYPE_CHECKING:
    from collections.abc import Callable

    from HABApp.rule_ctx import HABAppRuleContext


_HABAPP_RULE_CTX: Final[ContextVar[HABAppRuleContext]] = ContextVar('_habapp_rule_ctx')


class ContextBoundObj:
    def __init__(self, parent_ctx: Context | None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._parent_ctx: Context | None = parent_ctx
        if parent_ctx is not None:
            parent_ctx.add_obj(self)

    def _ctx_link(self, parent_ctx: Context) -> None:
        assert isinstance(parent_ctx, Context)
        if self._parent_ctx is not None:
            raise ContextBoundObjectIsAlreadyLinkedError()

        self._parent_ctx = parent_ctx
        parent_ctx.add_obj(self)

    def _ctx_unlink(self) -> None:
        if (parent := self._parent_ctx) is None:
            raise ContextBoundObjectIsAlreadyUnlinkedError()

        self._parent_ctx = None
        parent.remove_obj(self)


class Context:
    def __init__(self) -> None:
        self.objs: set[ContextBoundObj] = set()

    def add_obj(self, obj: ContextBoundObj) -> None:
        assert isinstance(obj, ContextBoundObj)
        self.objs.add(obj)

    def remove_obj(self, obj: ContextBoundObj) -> None:
        assert isinstance(obj, ContextBoundObj)
        self.objs.remove(obj)

    def link[O: ContextBoundObj](self, obj: O) -> O:
        assert isinstance(obj, ContextBoundObj)
        # noinspection PyProtectedMember
        obj._ctx_link(self)
        return obj

    def get_callback_name(self, callback: Callable) -> str | None:
        raise NotImplementedError()


class ContextProvidingObj:
    __slots__ = ('_habapp_ctx', )

    def __init__(self, context: Context | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._habapp_ctx: Context = context


def _wrap_with_rule_context[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """Wrap a function so that ``_HABAPP_RULE_CTX`` is set while the function is running.

    If the context is already set to the correct value (e.g. because we are already
    running inside a method of the same rule) we don't set the context again
    """

    if iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(self, *args: P.args, **kwargs: P.kwargs) -> R:
            ctx: Final = getattr(self, '_habapp_ctx', None)
            if _HABAPP_RULE_CTX.get(None) is ctx:
                return await func(self, *args, **kwargs)

            token: Final = _HABAPP_RULE_CTX.set(ctx)
            try:
                return await func(self, *args, **kwargs)
            finally:
                _HABAPP_RULE_CTX.reset(token)

        async_wrapper._habapp_ctx_wrapper = True
        return async_wrapper

    @wraps(func)
    def wrapper(self, *args: P.args, **kwargs: P.kwargs) -> R:
        ctx: Final = getattr(self, '_habapp_ctx', None)
        if _HABAPP_RULE_CTX.get(None) is ctx:
            return func(self, *args, **kwargs)

        token: Final = _HABAPP_RULE_CTX.set(ctx)
        try:
            return func(self, *args, **kwargs)
        finally:
            _HABAPP_RULE_CTX.reset(token)

    wrapper._habapp_ctx_wrapper = True
    return wrapper


def wrap_methods_with_cls_context(cls: type) -> None:
    # Wrap every function except ``__init__`` and functions that were already wrapped
    # use getmembers_static because it skips staticmethod/classmethod
    for name, value in getmembers_static(cls, predicate=isfunction):
        if name == '__init__' or getattr(value, '_habapp_ctx_wrapper', False):
            continue
        setattr(cls, name, _wrap_with_rule_context(value))
