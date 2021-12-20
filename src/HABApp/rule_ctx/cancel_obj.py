import HABApp


class RuleBoundCancelObj:
    """Object that can be canceled in a rule but will also be canceled when the rule is unloaded"""

    def __init__(self, rule_ctx=None):
        self._habapp_rule_ctx = HABApp.rule_ctx.get_rule_context(rule_ctx).add_cancel_object(self)

    def cancel(self):
        self._habapp_rule_ctx.remove_cancel_obj(self)
        self._habapp_rule_ctx = None
