import logging
from typing import Optional, Callable, Awaitable, Any, TYPE_CHECKING

from HABApp.core.asyncio import async_context, create_task
from .base import WrappedFunctionBaseImpl

if TYPE_CHECKING:
    import HABApp


TYPE_HINT_FUNC = Callable[..., Awaitable[Any]]


class WrappedAsyncFunction(WrappedFunctionBaseImpl):

    def __init__(self, func: TYPE_HINT_FUNC,
                 name: Optional[str] = None,
                 logger: Optional[logging.Logger] = None,
                 rule_ctx: Optional['HABApp.rule_ctx.HABAppRuleContext'] = None):

        super(WrappedAsyncFunction, self).__init__(name=name, func=func, logger=logger, rule_ctx=rule_ctx)
        assert callable(func)

        self.func = func

    def run(self, *args, **kwargs):
        create_task(self.async_run(*args, **kwargs), name=self.name)

    async def async_run(self, *args, **kwargs):

        token = async_context.set('WrappedAsyncFunction')

        try:
            await self.func(*args, **kwargs)
        except Exception as e:
            self.process_exception(e, *args, **kwargs)

        async_context.reset(token)
        return None
