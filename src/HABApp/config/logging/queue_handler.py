import logging
from queue import SimpleQueue, Empty
from threading import Thread, Lock
from time import sleep
from typing import Optional, Final

import HABApp
from .config import CONFIG

log = logging.getLogger('HABApp.logging')


LOCK = Lock()


class HABAppQueueHandler:
    FLUSH_DELAY: float = CONFIG.habapp.logging.flush_every

    def __init__(self, queue: SimpleQueue, handler_name: str, thread_name: str):
        self._handler: Optional[logging.Handler] = None
        self._handler_name: Final = handler_name
        self._queue: Final = queue
        self._name: Final = thread_name
        self._thread: Optional[Thread] = None

    def start(self) -> None:
        with LOCK:
            if self._thread is not None:
                raise RuntimeError('Thread can only be started once!')

            # resolve handler
            self._handler = logging._handlers[self._handler_name]

            self._thread = thread = Thread(target=self._worker, name=f'HABApp_{self._name}')

        thread.start()

    def signal_stop(self):
        self._queue.put_nowait(None)

    def stop(self) -> None:
        with LOCK:
            if (thread := self._thread) is None:
                return None

        self.signal_stop()
        thread.join()

    def _worker(self):
        try:
            log.debug(f'{self._name} thread running')

            try:
                assert self._handler is not None
                while True:
                    sleep(self.FLUSH_DELAY)
                    if self.process_queue():
                        break

            except Exception as e:
                HABApp.core.wrapper.process_exception(self._worker, e)

            # clean up queue
            try:
                while True:
                    self._queue.get_nowait()
            except Empty:
                pass

            log.debug(f'{self._name} thread stopped')
        finally:
            with LOCK:
                self._thread = None

    def process_queue(self) -> bool:
        q = self._queue
        handler = self._handler

        first_rec = True

        check_interval = 200
        ctr = check_interval

        skip_rem = 0
        skip_total = 0
        skip_level = logging.INFO

        try:
            while True:
                if first_rec:
                    # first call is blocking
                    rec = q.get()           # type: Optional[logging.LogRecord]
                    first_rec = False
                else:
                    rec = q.get_nowait()    # type: Optional[logging.LogRecord]

                if rec is None:
                    return True

                if skip_rem > 0:
                    # skip everything including INFO, process rest
                    if rec.levelno <= skip_level:
                        skip_rem -= 1
                        if skip_rem <= 0:
                            log.warning(f'Event log buffer congested! Skipped {skip_total} messages.')
                        continue

                # handle record
                handler.handle(rec)

                ctr -= 1
                if ctr <= 0:
                    ctr = check_interval
                    if not skip_rem:
                        q_size = q.qsize()
                        if q_size > 1000:
                            skip_total = skip_rem = q_size - 750

        except Empty:
            return False
