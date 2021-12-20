import sys

import HABApp


class RuleContextNotFoundError(Exception):
    pass


# @HABApp.core.wrapper.log_exception
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
                return getattr(obj, '_habapp_rule_ctx')
            except AttributeError:
                pass
