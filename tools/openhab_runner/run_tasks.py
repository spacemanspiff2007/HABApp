import logging
import subprocess
from collections.abc import Iterable
from itertools import chain
from types import TracebackType
from typing import Any, Self

from openhab_runner.models import RunConfig, TaskModel


log = logging.getLogger('task')
logs_log = logging.getLogger('logs')


class TaskHelper:
    def __init__(self) -> None:
        self._tasks: list[tuple[subprocess.Popen, str]] = []

    def __enter__(self) -> Self:
        return self

    def run_tasks(self, tasks: Iterable[TaskModel]) -> Self:
        for task in tasks:
            self.run_task(task)
        return self

    def run_task(self, task: TaskModel) -> Self:
        if (p := run_task(task)) is not None:
            self._tasks.append((p, task.name))
        return self

    def stop_tasks(self) -> Self:
        tasks = tuple(self._tasks)
        self._tasks.clear()

        to_terminate = []
        for task, name in tasks:
            task.poll()
            if task.returncode is None:
                to_terminate.append((task, name))
            else:
                log.debug(f'Task {name:s} exited with {task.returncode:d}')

        # Stop pending tasks
        for task, name in to_terminate:
            try:
                stop_task(task, name)
            except Exception as e:  # noqa: PERF203
                log.error(f'Error stopping task {name:s}: {e!s}')
                self._tasks.append((task, name))

        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None,
                 exc_tb: TracebackType | None) -> None:
        log.info('Stopping background tasks')
        self.stop_tasks()
        return None


def stop_task(task: subprocess.Popen, name: str) -> None:
    task.poll()
    task.terminate()
    try:
        task.wait(15)
    except TimeoutError:
        task.kill()

    if task.returncode is None:
        log.error(f'Task {name:s} did not terminate')
    elif task.returncode != 0:
        log.error(f'Task {name:s} failed with exit code {task.returncode:d}')
    else:
        log.info(f'Task {name:s} terminated')


def run_task(task: TaskModel) -> subprocess.Popen | None:
    task_args = [task.command, *(args if (args := task.args) else [])]
    log.info('')
    log.debug(f'Running {" ".join(task_args)}')

    kwargs: dict[str, Any] = {}

    if (_env := task.env) is not None:
        kwargs['env'] = _env

    if (_cwd := task.cwd) is not None:
        kwargs['cwd'] = _cwd

    if (_shell := task.shell) is not None:
        kwargs['shell'] = _shell

    if (_timeout := task.timeout) is not None:
        kwargs['timeout'] = _timeout

    if task.new_console or not task.wait:
        kwargs['creationflags'] = subprocess.CREATE_NEW_CONSOLE

    if not task.wait:
        return subprocess.Popen(task_args, **kwargs)  # noqa: S603

    ret = subprocess.run(task_args, **kwargs,  # noqa: S603
                         capture_output=True, text=True, check=False)
    if ret.returncode == 0:
        log.info(f'{task.name}:')
        lvl = logging.INFO
    else:
        log.info(f'{task.name} failed with exit code {ret.returncode}:')
        lvl = logging.ERROR

    for line in chain(ret.stderr.splitlines(), ret.stdout.splitlines()):
        log.log(lvl, line)

    if ret.returncode != 0:
        raise subprocess.CalledProcessError(ret.returncode, args, ret.stdout, ret.stderr)
    return None


def run_openhab(runner: RunConfig) -> None:
    logs_log.debug('')
    logs_log.debug('Removing log files')
    for obj in runner.openhab_logs.iterdir():
        if obj.is_file():
            logs_log.debug(f'Removing {obj}')
            obj.unlink()

    oh_task = run_task(runner.openhab_task)
    log.info('Waiting for openHAB to exit')
    oh_task.communicate()
    log.debug(f'openHAB exited with {oh_task.returncode}')
