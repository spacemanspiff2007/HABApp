import sys
from typing import Optional, Union, TYPE_CHECKING

from HABApp.core.errors import ContextNotSetError, ContextNotFoundError
from HABApp.core.internals.context import ContextProvidingObj, ContextBoundObj, HINT_CONTEXT_OBJ

if TYPE_CHECKING:
    import HABApp
    import types


def get_current_context(obj: Optional[ContextProvidingObj] = None) -> 'HABApp.rule_ctx.HABAppRuleContext':
    if obj is not None:
        return obj._habapp_ctx

    depth = 0
    while True:
        depth += 1
        try:
            frm = sys._getframe(depth)  # type: types.FrameType
        except ValueError:
            raise ContextNotFoundError() from None

        ctx_obj: Union[None, object, ContextProvidingObj] = frm.f_locals.get('self', None)
        if ctx_obj is None or not isinstance(ctx_obj, ContextProvidingObj):
            continue

        ctx = ctx_obj._habapp_ctx
        if ctx is None:
            raise ContextNotSetError()
        return ctx


class AutoContextBoundObj(ContextBoundObj):
    def __init__(self, parent_ctx: Optional['HINT_CONTEXT_OBJ'] = None, **kwargs):
        if parent_ctx is None:
            parent_ctx = get_current_context()
        super().__init__(parent_ctx=parent_ctx, **kwargs)
