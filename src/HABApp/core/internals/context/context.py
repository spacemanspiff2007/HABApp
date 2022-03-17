from typing import Set, Optional
from typing import TypeVar

from HABApp.core.errors import ContextBoundObjectIsAlreadyLinkedError, ContextBoundObjectIsAlreadyUnlinkedError


class ContextBoundObj:
    def __init__(self, parent_ctx: Optional['TYPE_CONTEXT_OBJ'], **kwargs):
        super().__init__(**kwargs)
        self._parent_ctx = parent_ctx
        if parent_ctx is not None:
            parent_ctx.add_obj(self)

    def _ctx_link(self, parent_ctx: 'TYPE_CONTEXT_OBJ'):
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


TYPE_CONTEXT_BOUND_OBJ = TypeVar('TYPE_CONTEXT_BOUND_OBJ', bound=ContextBoundObj)


class Context:
    def __init__(self):
        self.objs: Set[TYPE_CONTEXT_BOUND_OBJ] = set()

    def add_obj(self, obj: TYPE_CONTEXT_BOUND_OBJ):
        assert isinstance(obj, ContextBoundObj)
        self.objs.add(obj)

    def remove_obj(self, obj: TYPE_CONTEXT_BOUND_OBJ):
        assert isinstance(obj, ContextBoundObj)
        self.objs.remove(obj)

    def link(self, obj: TYPE_CONTEXT_BOUND_OBJ) -> TYPE_CONTEXT_BOUND_OBJ:
        assert isinstance(obj, ContextBoundObj)
        obj._ctx_link(self)
        return obj

    def get_callback_name(self, callback: callable) -> Optional[str]:
        raise NotImplementedError()


TYPE_CONTEXT_OBJ = TypeVar('TYPE_CONTEXT_OBJ', bound=Context)


class ContextMixin:
    def __init__(self, context: Optional[TYPE_CONTEXT_OBJ] = None, **kwargs):
        super().__init__(**kwargs)
        self._habapp_ctx: TYPE_CONTEXT_OBJ = context
