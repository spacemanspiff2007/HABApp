from __future__ import annotations

import traceback

# noinspection PyProtectedMember
from sys import _getframe as sys_get_frame
from typing import TYPE_CHECKING, Any, Final

from HABApp.core.errors import ContextNotFoundError, ContextNotSetError
from HABApp.core.internals.context import Context, ContextBoundObj, ContextProvidingObj
from HABApp.core.internals.context.context import _HABAPP_RULE_CTX


if TYPE_CHECKING:
    from types import FrameType

    from HABApp.rule_ctx import HABAppRuleContext


def _in_rule_init(frame: FrameType) -> bool:
    from HABApp.rule.rule import Rule  # noqa: PLC0415

    while frame is not None:
        if frame.f_code.co_name == '__init__' and isinstance(frame.f_locals.get('self'), Rule):
            return True
        frame = frame.f_back
    return False


def get_current_context_or_none() -> HABAppRuleContext | None:
    return _HABAPP_RULE_CTX.get()


# noinspection PyProtectedMember
def get_current_context() -> HABAppRuleContext:
    # Context is already set, this is the default path
    if (var_ctx := _HABAPP_RULE_CTX.get()) is not None:
        return var_ctx

    this_frame: Final = sys_get_frame(1)
    frame: FrameType | None = this_frame
    ctx_obj: ContextProvidingObj | None = None

    while frame is not None:
        ctx_obj = frame.f_locals.get('self')
        if ctx_obj is not None and isinstance(ctx_obj, ContextProvidingObj):
            break

        frame = frame.f_back

    if frame is None:
        msg = f'No context found!:\n{"".join(traceback.format_stack(this_frame))}'
        raise ContextNotFoundError(msg)

    # if we access _habapp_ctx before __init__ it does not exist. With getattr it works every time
    ctx: HABAppRuleContext | None = getattr(ctx_obj, '_habapp_ctx', None)
    if ctx is None:
        if _in_rule_init(frame):
            msg = 'Context is not set! When overriding __init__ make sure to call super().__init__() first.'
            raise ContextNotSetError(msg)

        # this can only happen if we have a partially loaded/unloaded rule
        raise ContextNotSetError()

    # Todo: check this once we removed the frame walking
    # # The only time when we end up here is when a rule is being constructed and we call something from __init__
    # # If we are not in __init__ something went very wrong
    # if not in_rule_init:
    #     msg = (
    #         f'Frame-walk fallback was used outside of __init__ for '
    #         f'{type(ctx_obj).__name__} in "{frame.f_code.co_name}" '
    #         f'({frame.f_code.co_filename}:{frame.f_lineno}). '
    #         f'This means _habapp_rule_ctx was not set correctly!'
    #     )
    #     raise RuntimeError(msg)

    return ctx


class AutoContextBoundObj(ContextBoundObj):
    def __init__(self, parent_ctx: Context | None = None, **kwargs: Any) -> None:
        if parent_ctx is None:
            parent_ctx = get_current_context()
        super().__init__(parent_ctx=parent_ctx, **kwargs)
