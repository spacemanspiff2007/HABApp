from asyncio import run_coroutine_threadsafe

from HABApp.core.const import loop
from HABApp.core.asyncio import async_context
from eascheduler.jobs.job_base import ScheduledJobBase
from eascheduler.schedulers import AsyncScheduler


class HABAppScheduler(AsyncScheduler):
    def __init__(self):
        super().__init__()

        # we start paused, so we execute stuff only if we can load the whole file properly
        self.pause()

    async def _run_next(self):
        async_context.set('HABAppScheduler')
        return await super()._run_next()

    async def __add_job(self, job: ScheduledJobBase):
        super().add_job(job)

    async def __remove_job(self, job: ScheduledJobBase):
        super().remove_job(job)

    async def __cancel_all(self):
        super().cancel_all()

    async def __pause(self):
        super().pause()

    async def __resume(self):
        super().resume()

    def pause(self):
        if async_context.get(None) is None:
            run_coroutine_threadsafe(self.__pause(), loop).result()
        else:
            super().pause()
        return None

    def resume(self):
        if async_context.get(None) is None:
            run_coroutine_threadsafe(self.__resume(), loop).result()
        else:
            super().resume()
        return None

    def add_job(self, job: ScheduledJobBase):
        if async_context.get(None) is None:
            run_coroutine_threadsafe(self.__add_job(job), loop).result()
        else:
            super().add_job(job)
        return None

    def remove_job(self, job: ScheduledJobBase):
        if async_context.get(None) is None:
            run_coroutine_threadsafe(self.__remove_job(job), loop).result()
        else:
            super().remove_job(job)
        return None

    def cancel_all(self):
        if async_context.get(None) is None:
            run_coroutine_threadsafe(self.__cancel_all(), loop).result()
        else:
            super().cancel_all()
        return None
