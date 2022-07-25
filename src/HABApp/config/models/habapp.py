from pydantic import Field, conint

from easyconfig import BaseModel


class ThreadPoolConfig(BaseModel):
    enabled: bool = True
    """When the thread pool is disabled HABApp will become an asyncio application.
    Use only if you have experience developing asyncio applications!
    If the thread pool is disabled using blocking calls in functions can and will break HABApp"""

    threads: conint(ge=1, le=16) = 10
    """Amount of threads to use for the executor"""


class LoggingConfig(BaseModel):
    use_buffer: bool = Field(True, alias='use buffer')
    """Automatically inject a buffer for the event log"""

    flush_every: float = Field(0.5, alias='flush every', ge=0.1)
    """Wait time in seconds before the buffer gets flushed again when it was empty"""


class HABAppConfig(BaseModel):
    """HABApp internal configuration. Only change values if you know what you are doing!"""

    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    thread_pool: ThreadPoolConfig = Field(default_factory=ThreadPoolConfig, alias='thread pool')
