
import logging
import time
from asyncio import Future, create_task, sleep
from pathlib import Path
from typing import Optional

import HABApp
from HABApp.core.files.file import FileState
from HABApp.core.files.folders import get_prefixes
from . import FILES

log = logging.getLogger('HABApp.files')


TASK: Optional[Future] = None
TASK_SLEEP: float = 0.3
TASK_DURATION: float = 15


async def process_file(name: str, file: Path):
    global TASK

    # unload file
    if not file.is_file():
        existing = FILES.pop(name, None)
        if existing is None:
            return None

        await existing.unload()
        log.debug(f'Removed {existing.name}')
        return None

    # add file
    FILES[name] = HABApp.core.files.file.create_file(name, file)
    if TASK is None:
        TASK = create_task(_process())


async def _process():
    global TASK

    prefixes = get_prefixes()

    ct = -1
    log_msg = False
    last_process = time.time()

    try:
        while True:

            # wait until files are stable
            while ct != len(FILES):
                ct = len(FILES)
                await sleep(TASK_SLEEP)

            # check files for dependencies etc.
            for file in FILES.values():
                file.check_properties(log_msg)

            # Load order
            for prefix in prefixes:
                file_loaded = False
                for name in filter(lambda x: x.startswith(prefix), sorted(FILES.keys())):
                    file = FILES[name]
                    file.check_dependencies()

                    if file.state is FileState.DEPENDENCIES_OK:
                        await file.load()
                        last_process = time.time()
                        file_loaded = True
                        break
                if file_loaded:
                    break

            # if we don't have any files left to load we sleep!
            if not any(map(lambda x: x.state is FileState.DEPENDENCIES_OK, FILES.values())):
                await sleep(TASK_SLEEP)

            # Emit an error message during the last run
            if log_msg:
                break
            log_msg = time.time() - last_process > TASK_DURATION

    except Exception as e:
        HABApp.core.wrapper.process_exception('file load worker', e, logger=log)
    finally:
        TASK = None
    log.debug('Worker done!')
