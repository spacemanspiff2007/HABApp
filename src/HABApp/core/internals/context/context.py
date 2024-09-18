from collections.abc import Callable
from typing import Optional, TypeVar

from HABApp.core.errors import ContextBoundObjectIsAlreadyLinkedError, ContextBoundObjectIsAlreadyUnlinkedError


class ContextBoundObj:
    def __init__(self, parent_ctx: Optional['Context'], **kwargs):
        super().__init__(**kwargs)
        self._parent_ctx = parent_ctx
        if parent_ctx is not None:
            parent_ctx.add_obj(self)

    def _ctx_link(self, parent_ctx: 'Context'):
        assert isinstance(parent_ctx, Context)
        if self._parent_ctx is not None:
            raise ContextBoundObjectIsAlreadyLinkedError()

        self._parent_ctx = parent_ctx
        parent_ctx.add_obj(self)

    def _ctx_unlink(self):
        if self._parent_ctx is None:
            raise ContextBoundObjectIsAlreadyUnlinkedError()

        self._parent_ctx.remove_obj(self)
        self._parent_ctx = None


HINT_CONTEXT_BOUND_OBJ = TypeVar('HINT_CONTEXT_BOUND_OBJ', bound=ContextBoundObj)


class Context:
    def __init__(self):
        self.objs: set[ContextBoundObj] = set()

    def add_obj(self, obj: ContextBoundObj):
        assert isinstance(obj, ContextBoundObj)
        self.objs.add(obj)

    def remove_obj(self, obj: ContextBoundObj):
        assert isinstance(obj, ContextBoundObj)
        self.objs.remove(obj)

    def link(self, obj: HINT_CONTEXT_BOUND_OBJ) -> HINT_CONTEXT_BOUND_OBJ:
        assert isinstance(obj, ContextBoundObj)
        # noinspection PyProtectedMember
        obj._ctx_link(self)
        return obj

    def get_callback_name(self, callback: Callable) -> str | None:
        raise NotImplementedError()


class ContextProvidingObj:
    def __init__(self, context: Context | None = None, **kwargs):
        super().__init__(**kwargs)
        self._habapp_ctx: Context = context
