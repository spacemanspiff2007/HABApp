import asyncio


class FinishedProcessInfo:
    """Information about the finished process."""


    def __init__(self, returncode: int, stdout: str, stderr: str):
        self.returncode: int = returncode
        self.stdout: str = stdout
        self.stderr: str = stderr

    def __repr__(self):
        return f'<ProcessInfo: returncode:{self.returncode} stdout:{self.stdout} stderr:{self.stderr}>'


async def async_subprocess_exec(callback, program: str, *args, capture_output=True):
    assert isinstance(program, str), type(program)

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

        stdout, stderr = await proc.communicate()
        stdout = stdout.decode()
        stderr = stderr.decode()
        ret_code = proc.returncode
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
