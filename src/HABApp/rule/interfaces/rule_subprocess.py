import asyncio
import os
from pathlib import Path
from typing import Optional, Union, Iterable, Any, Tuple, Dict, List

from typing_extensions import TypeAlias

HINT_EXEC_ARGS: TypeAlias = Union[str, Path]
HINT_PYTHON_PATH: TypeAlias = Optional[Iterable[Union[str, Path]]]


def build_exec_params(*args: Iterable[HINT_EXEC_ARGS],
                      _capture_output=True,
                      _additional_python_path: HINT_PYTHON_PATH = None,
                      **kwargs: Any) -> Tuple[Iterable[str], Dict[str, Any]]:
    new_args: List[str] = []

    # args must be str, but we support str and Path
    for i, arg in enumerate(args):
        if isinstance(arg, Path):
            new_args.append(str(arg))
            continue
        if not isinstance(arg, str):
            raise ValueError(f'Arg {i:d} "{arg}" is not of type str! ({type(arg)})')
        new_args.append(arg)

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

        to_add: List[str] = []
        for _ppath in _additional_python_path:
            if isinstance(_ppath, str):
                _ppath = Path(_ppath)
            if not _ppath.is_dir():
                raise FileNotFoundError(f'Additional python path folder "{_ppath}" does not exist!')
            to_add.append(str(_ppath))

        # The child process needs the env from the current process, that's why we merge them
        # See docs of subprocess.Popen -> env for more details
        env = dict(os.environ)
        existing_ppath = env.get('PYTHONPATH')
        if existing_ppath:
            to_add.append(existing_ppath)
        env['PYTHONPATH'] = os.pathsep.join(to_add)
        kwargs['env'] = env

    return new_args, kwargs


class FinishedProcessInfo:
    """Information about the finished process."""

    def __init__(self, returncode: int, stdout: Optional[str], stderr: Optional[str]):
        self.returncode: int = returncode
        self.stdout: Optional[str] = stdout
        self.stderr: Optional[str] = stderr

    def __repr__(self):
        return f'<ProcessInfo: returncode: {self.returncode}, stdout: {self.stdout}, stderr: {self.stderr}>'


async def async_subprocess_exec(callback, program: Union[str, Path], *args, **kwargs):
    try:
        assert isinstance(program, (str, Path, bytes)), type(program)

        proc = None
        stdout = None
        stderr = None

        try:
            proc = await asyncio.create_subprocess_exec(program, *args, **kwargs)

            b_stdout, b_stderr = await proc.communicate()
            ret_code = proc.returncode

            if b_stdout or b_stderr:
                stdout = b_stdout.decode()
                stderr = b_stderr.decode()

        except asyncio.CancelledError as e:
            if proc is not None:
                proc.terminate()

            ret_code = -2
            stdout = 'Task cancelled'
            stderr = f'{type(e).__name__:s}'

    except Exception as e:
        ret_code = -1
        stdout = 'Error during process handling!'
        stderr = f'{type(e).__name__:s}: {e}'

    # callback is a wrapped function, that's why it will not throw an error
    callback(FinishedProcessInfo(ret_code, stdout, stderr))
    return None
