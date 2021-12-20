import sys

import HABApp


class RuleContextNotFoundError(Exception):
    pass


class RuleContextNotSetError(Exception):
    pass


def get_rule_context(obj=None) -> 'HABApp.rule_ctx.HABAppRuleContext':
    if obj is not None:
        return getattr(obj, '_habapp_rule_ctx')

    depth = 1
    while True:
        try:
            frm = sys._getframe(depth)
        except ValueError:
            raise RuleContextNotFoundError() from None

        locals_vars = frm.f_locals
        depth += 1
        if 'self' in locals_vars:
            obj = locals_vars['self']
            try:
                # For some objects the rule context ist optional
                ctx = getattr(obj, '_habapp_rule_ctx')
                if ctx is None:
                    raise RuleContextNotSetError()
                return ctx
            except AttributeError:
                pass
