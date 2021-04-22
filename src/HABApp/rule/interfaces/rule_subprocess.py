import asyncio
import typing


class FinishedProcessInfo:
    """Information about the finished process."""

    def __init__(self, returncode: int, stdout: typing.Optional[str], stderr: typing.Optional[str]):
        self.returncode: int = returncode
        self.stdout: typing.Optional[str] = stdout
        self.stderr: typing.Optional[str] = stderr

    def __repr__(self):
        return f'<ProcessInfo: returncode: {self.returncode}, stdout: {self.stdout}, stderr: {self.stderr}>'


async def async_subprocess_exec(callback, program: str, *args, capture_output=True):
    assert isinstance(program, str), type(program)

    proc = None
    stdout = None
    stderr = None
    ret_code = None

    try:
        proc = await asyncio.create_subprocess_exec(
            program,
            *args,
            stdout=asyncio.subprocess.PIPE if capture_output else None,
            stderr=asyncio.subprocess.PIPE if capture_output else None
        )

        b_stdout, b_stderr = await proc.communicate()
        ret_code = proc.returncode
        if capture_output:
            stdout = b_stdout.decode()
            stderr = b_stderr.decode()
    except asyncio.CancelledError:
        if proc is not None:
            proc.terminate()

        stdout = None
        stderr = None
        ret_code = -2
    except Exception as e:
        ret_code = -1
        stderr = str(e)

    callback(FinishedProcessInfo(ret_code, stdout, stderr))
    return None
