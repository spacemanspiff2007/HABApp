from __future__ import annotations

import traceback

# noinspection PyProtectedMember
from sys import _getframe as sys_get_frame
from typing import TYPE_CHECKING, Any, Final

from HABApp.core.errors import ContextNotFoundError, ContextNotSetError
from HABApp.core.internals.context import Context, ContextBoundObj, ContextProvidingObj


if TYPE_CHECKING:
    from types import FrameType

    import HABApp


# noinspection PyProtectedMember
def get_current_context(obj: ContextProvidingObj | None = None) -> HABApp.rule_ctx.HABAppRuleContext:
    if obj is not None:
        return obj._habapp_ctx

    this_frame: Final = sys_get_frame(1)
    frame: FrameType | None = this_frame

    while frame is not None:

        ctx_obj: None | object | ContextProvidingObj = frame.f_locals.get('self')
        if ctx_obj is not None and isinstance(ctx_obj, ContextProvidingObj):
            ctx = ctx_obj._habapp_ctx
            if ctx is None:
                raise ContextNotSetError()
            return ctx

        frame = frame.f_back

    msg = f'No context found!:\n{"".join(traceback.format_stack(this_frame))}'
    raise ContextNotFoundError(msg)


class AutoContextBoundObj(ContextBoundObj):
    def __init__(self, parent_ctx: Context | None = None, **kwargs: Any) -> None:
        if parent_ctx is None:
            parent_ctx = get_current_context()
        super().__init__(parent_ctx=parent_ctx, **kwargs)
