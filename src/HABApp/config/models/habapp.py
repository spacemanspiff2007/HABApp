from datetime import timedelta

from easyconfig import BaseModel
from pydantic import Field, model_validator
from typing_extensions import Self


class ThreadPoolConfig(BaseModel):
    enabled: bool = Field(
        True,
        description='When the thread pool is disabled HABApp will become an asyncio application. '
        'Use only if you have experience developing asyncio applications! '
        'If the thread pool is disabled using blocking calls in functions can and will break HABApp',
    )
    threads: int = Field(10, ge=1, le=32, description='Amount of threads to use for the executor')


class LoggingConfig(BaseModel):
    use_buffer: bool = Field(True, alias='use buffer', description='Automatically inject a buffer for the event log')
    flush_every: float = Field(
        0.5,
        alias='flush every',
        ge=0.1,
        description='Wait time in seconds before the buffer gets flushed again when it was empty',
    )


class PeriodicTracebackDumpConfig(BaseModel):
    """Periodically dump the traceback of all currently running threads into a file"""

    enabled: bool = Field(False, description='Enable or disable functionality')
    delay: timedelta = Field(
        timedelta(minutes=30),  # PT30M,
        gt=timedelta(seconds=0),
        description='Initial delay before the first traceback dump',
    )
    interval: timedelta = Field(
        timedelta(hours=1),  # PT1H
        gt=timedelta(seconds=0),
        description='Interval to dump the traceback',
    )


class WatchEventLoopConfig(BaseModel):
    """Watch the asyncio event loop. If the loop is blocked dump the traceback of all running threads
    and shut down HABApp"""

    enabled: bool = Field(False, description='Enable or disable functionality')
    reset_every: timedelta = Field(
        timedelta(minutes=1),  # PT1M
        alias='reset every',
        gt=timedelta(seconds=0),
        description='Reset interval for the timeout',
    )
    timeout: timedelta = Field(
        timedelta(minutes=2, seconds=30),  # PT2M30
        gt=timedelta(seconds=0),
        description='Timeout after which HABApp will shut down',
    )

    @model_validator(mode='after')
    def _check_values(self) -> Self:
        # round to second
        self.timeout = timedelta(seconds=round(self.timeout.total_seconds()))
        self.reset_every = timedelta(seconds=round(self.reset_every.total_seconds()))

        if self.timeout <= self.reset_every:
            msg = f'Timeout must be greater than reset time! {self.timeout} > {self.reset_every}'
            raise ValueError(msg)
        return self


class DebugConfig(BaseModel):
    """Debugging options for HABApp"""

    periodic_traceback: PeriodicTracebackDumpConfig = Field(
        alias='periodic traceback', default_factory=PeriodicTracebackDumpConfig
    )

    traceback_on_shutdown_signal: bool = Field(
        False,
        alias='traceback on shutdown signal',
        description='Dump the traceback of all currently running threads into a file when receiving a shutdown signal. '
        'Not available on Windows!',
    )

    watch_event_loop: WatchEventLoopConfig = Field(alias='watch event loop', default_factory=WatchEventLoopConfig)


class HABAppConfig(BaseModel):
    """HABApp internal configuration. Only change values if you know what you are doing!"""

    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    thread_pool: ThreadPoolConfig = Field(default_factory=ThreadPoolConfig, alias='thread pool')
    debug: DebugConfig = Field(default_factory=DebugConfig)
