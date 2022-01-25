import asyncio
import logging
import signal
import sys
import traceback
import typing


import HABApp
from HABApp.__cmd_args__ import parse_args, find_config_folder
from HABApp.__splash_screen__ import show_screen
from HABApp.__debug_info__ import print_debug_info


def register_signal_handler():
    def shutdown_handler(sig, frame):
        print('Shutting down ...')
        HABApp.runtime.shutdown.request_shutdown()

    # register shutdown helper
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)


def main() -> typing.Union[int, str]:

    show_screen()

    # This has do be done before we create HABApp because of the possible sleep time
    args = parse_args()

    if HABApp.__cmd_args__.DO_DEBUG:
        print_debug_info()
        sys.exit(0)

    log = logging.getLogger('HABApp')

    cfg_folder = find_config_folder(args.config)

    try:
        app = HABApp.runtime.Runtime()
        register_signal_handler()

        HABApp.core.const.loop.create_task(app.start(cfg_folder))
        HABApp.core.const.loop.run_forever()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        for line in traceback.format_exc().splitlines():
            log.error(line)
            print(e)
        return str(e)
    finally:
        # Sleep to allow underlying connections of aiohttp to close
        # https://aiohttp.readthedocs.io/en/stable/client_advanced.html#graceful-shutdown
        HABApp.core.const.loop.run_until_complete(asyncio.sleep(1))
        HABApp.core.const.loop.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
