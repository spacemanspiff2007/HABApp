import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, Union, Iterable, Any, Tuple, Dict, List, Callable

from typing_extensions import TypeAlias

import HABApp
from HABApp.core.logger import HABAppError, HABAppWarning
from HABApp.core.wrapper import process_exception

log = logging.getLogger('HABApp.execute')

HINT_EXEC_ARGS: TypeAlias = Union[str, Path]
HINT_PYTHON_PATH: TypeAlias = Optional[Iterable[Union[str, Path]]]


def _ensure_str_objs(objs: Iterable[HINT_EXEC_ARGS], key: str, enforce_abs=False) -> List[str]:
    new_args: List[str] = []

    # args must be str, but we support str and Path
    for i, val in enumerate(objs):
        if isinstance(val, Path):
            path_val = val
            str_val = str(val)
        elif isinstance(val, str):
            path_val = Path(val)
            str_val = val
        else:
            raise ValueError(f'{key:s}[{i:d}] is not of type str! "{val}" ({type(val).__name__:s})')

        if enforce_abs and not path_val.is_absolute():
            raise ValueError(f'{key:s}[{i:d}] is not an absolute path: "{val}"')

        new_args.append(str_val)

    return new_args


def build_exec_params(*args: HINT_EXEC_ARGS,
                      _capture_output=True,
                      _additional_python_path: HINT_PYTHON_PATH = None,
                      **kwargs: Any) -> Tuple[Iterable[str], Dict[str, Any]]:

    # convenience for easy capturing
    if _capture_output:
        if 'stdout' in kwargs:
            raise ValueError('Parameter "capture_output" can not be used with "stdout" in kwargs!')
        kwargs['stdout'] = asyncio.subprocess.PIPE
        if 'stderr' in kwargs:
            raise ValueError('Parameter "capture_output" can not be used with "stderr" in kwargs!')
        kwargs['stderr'] = asyncio.subprocess.PIPE

    # convenience for additional libraries
    if _additional_python_path is not None:
        if 'env' in kwargs:
            raise ValueError('Parameter "additional_python_path" can not be used with "env" in kwargs!')

        ppath = _ensure_str_objs(_additional_python_path, 'additional_python_path', enforce_abs=True)

        # The child process needs the env from the current process, that's why we merge them
        # See docs of subprocess.Popen -> env for more details
        env = dict(os.environ)

        existing_ppath = env.get('PYTHONPATH')
        if existing_ppath:
            ppath.append(existing_ppath)
        env['PYTHONPATH'] = os.pathsep.join(ppath)
        kwargs['env'] = env

    # set config folder as working directory
    if 'cwd' not in kwargs:
        kwargs['cwd'] = HABApp.CONFIG._file_path.parent

    return _ensure_str_objs(args, 'args'), kwargs


class FinishedProcessInfo:
    """Information about the finished process.

    :var int returncode: Return code of the process
    :var Optional[str] stdout: Standard output of the process or ``None``
    :var Optional[str] stderr: Error output of the process or ``None``
    """

    def __init__(self, returncode: int, stdout: Optional[str], stderr: Optional[str]):
        self.returncode: int = returncode
        self.stdout: Optional[str] = stdout
        self.stderr: Optional[str] = stderr

    def __repr__(self):
        return f'<ProcessInfo: returncode: {self.returncode}, stdout: {self.stdout}, stderr: {self.stderr}>'

    def __eq__(self, other):
        if isinstance(other, FinishedProcessInfo):
            return self.returncode == other.returncode and self.stdout == other.stdout and self.stderr == other.stderr
        else:
            return NotImplementedError


HINT_PROCESS_CB_FULL: TypeAlias = Callable[[FinishedProcessInfo], Any]
HINT_PROCESS_CB_SIMPLE: TypeAlias = Callable[[str], Any]


async def async_subprocess_exec(callback, *args, calling_func, raw_info: bool, **kwargs):

    call_str = ''

    try:

        proc = None
        stdout = None
        stderr = None

        call_str = ' '.join(map(lambda x: f'"{x}"', args))

        try:
            proc = await asyncio.create_subprocess_exec(*args, **kwargs)

            b_stdout, b_stderr = await proc.communicate()
            ret_code = proc.returncode

            if b_stdout or b_stderr:
                stdout = b_stdout.decode()
                stderr = b_stderr.decode()

        except asyncio.CancelledError:
            if proc is not None:
                proc.terminate()

            HABAppWarning(log=log).add(f'Subprocess canceled! Call: {call_str}').dump()
            return None

    except FileNotFoundError as e:
        HABAppError(log=log).add('Creating subprocess failed!').add(f'  Call: {call_str}').add(
            f'  Working dir: {kwargs.get("cwd")}').add(str(e)).dump()
        return None
    except Exception as e:
        HABAppError(log=log).add('Creating subprocess failed!').add(f'  Call: {call_str}').add(
            f'  Working dir: {kwargs.get("cwd")}').dump()
        process_exception(calling_func, e, logger=log)
        return None

    if raw_info:
        # callback is a wrapped function, that's why it will not throw an error
        callback(FinishedProcessInfo(ret_code, stdout, stderr))
        return None

    if ret_code != 0:
        e = HABAppError(log=log).add(f'Process returned {ret_code:d}!').add(f'Call: {call_str}')
        if stderr:
            e.add('Stderr:')
            for line in stderr.splitlines():
                e.add(f'  {line}')
        elif stdout:
            e.add('Stdout:')
            for line in stdout.splitlines():
                e.add(f'  {line}')
        e.dump()
        return None

    # no error -> callback always with str
    callback(stdout if stdout else '')
    return None
