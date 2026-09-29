from typing import TYPE_CHECKING, Final, override

from eascheduler.schedulers.async_scheduler import AsyncScheduler
from whenever import Instant

from HABApp.config import ApplicationConfig
from HABApp.testing.time import AsyncioTestingProvider


if TYPE_CHECKING:
    from asyncio import Task


class TestingScheduler(AsyncScheduler):
    """Scheduler for testing that uses AsyncioTestingProvider for time keeping.

    Jobs are triggered through the testing provider's sleep mechanism, enabling deterministic time-travel.
    """

    def __init__(self, asyncio_provider: AsyncioTestingProvider) -> None:
        super().__init__(event_loop=asyncio_provider.loop)
        self._asyncio: Final = asyncio_provider
        self._task: Task | None = None

    @override
    def _set_timer(self) -> None:
        if (task := self._task) is not None:
            self._task = None
            task.cancel()

        if not self.jobs or not self._enabled:
            return None

        next_run: Instant | None = self.jobs[0].next_run
        if next_run is None:
            return None

        if next_run <= Instant.now():
            self.run_jobs()
        else:
            self._task = self._asyncio.create_task(
                self._wait_and_run(next_run), name='TestingScheduler._wait_and_run'
            )
        return None

    async def _wait_and_run(self, target: Instant) -> None:
        await self._asyncio.sleep(target)
        # create_task holds a reference to the task that's why we can set it to None here
        self._task = None
        self.run_jobs()


def get_location(cfg: ApplicationConfig | None) -> tuple[float, float, float]:
    if cfg is None:
        return 52.51870523376821, 13.376072914752532, 10
    loc_cfg: Final = cfg.location
    return loc_cfg.latitude, loc_cfg.longitude, loc_cfg.elevation


def get_holiday(cfg: ApplicationConfig | None) -> tuple[str, str]:
    if cfg is None:
        return 'DE', 'BE'

    loc_cfg: Final = cfg.location
    if not loc_cfg.country:
        return 'DE', 'BE'

    return loc_cfg.country, loc_cfg.subdivision
