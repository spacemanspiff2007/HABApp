import sys
import asyncio


# otherwise creating a subprocess does not work on windows
if sys.platform == "win32":
    # This is the default from 3.8 so we don't have to set it ourselves
    if sys.version_info < (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
else:
    # Must be called once in the main thread so creating a subprocess works properly
    # https://docs.python.org/3/library/asyncio-subprocess.html#subprocess-and-threads
    asyncio.get_child_watcher()

loop = asyncio.get_event_loop()
loop.set_debug(True)
loop.slow_callback_duration = 0.02
