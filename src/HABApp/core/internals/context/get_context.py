# noinspection PyProtectedMember
from sys import _getframe as sys_get_frame
from types import FrameType
from typing import Optional, Union, TYPE_CHECKING

from HABApp.core.errors import ContextNotSetError, ContextNotFoundError
from HABApp.core.internals.context import ContextProvidingObj, ContextBoundObj, Context

if TYPE_CHECKING:
    import HABApp


# noinspection PyProtectedMember
def get_current_context(obj: Optional[ContextProvidingObj] = None) -> 'HABApp.rule_ctx.HABAppRuleContext':
    if obj is not None:
        return obj._habapp_ctx

    frame: Optional[FrameType] = sys_get_frame(1)

    while frame is not None:

        ctx_obj: Union[None, object, ContextProvidingObj] = frame.f_locals.get('self')
        if ctx_obj is not None and isinstance(ctx_obj, ContextProvidingObj):
            ctx = ctx_obj._habapp_ctx
            if ctx is None:
                raise ContextNotSetError()
            return ctx

        frame = frame.f_back

    raise ContextNotFoundError()


class AutoContextBoundObj(ContextBoundObj):
    def __init__(self, parent_ctx: Optional['Context'] = None, **kwargs):
        if parent_ctx is None:
            parent_ctx = get_current_context()
        super().__init__(parent_ctx=parent_ctx, **kwargs)
