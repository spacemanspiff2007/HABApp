import logging

from pydantic import Field, conint

from easyconfig import BaseModel

log = logging.getLogger('HABApp.Config')


class ThreadPoolConfig(BaseModel):
    enabled: bool = True
    """When the thread pool is disabled HABApp will become an asyncio application.
    Use only if you have experience developing asyncio applications!
    If active using blocking calls in functions can and will break HABApp"""

    threads: conint(ge=0, le=16) = 10
    """Amount of threads to use for the executor"""


class HABAppConfig(BaseModel):
    """HABApp internal configuration. Only change values if you know what you are doing!"""

    thread_pool: ThreadPoolConfig = Field(default_factory=ThreadPoolConfig, alias='thread pool')
