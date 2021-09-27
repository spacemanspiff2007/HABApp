import asyncio
import logging
import signal
import sys
import traceback
import typing

import HABApp
from HABApp.__cmd_args__ import parse_args


def register_signal_handler():
    def shutdown_handler(sig, frame):
        print('Shutting down ...')
        HABApp.runtime.shutdown.request_shutdown()

    # register shutdown helper
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)


def main() -> typing.Union[int, str]:

    # This has do be done before we create HABApp because of the possible sleep time
    cfg_folder = parse_args()

    log = logging.getLogger('HABApp')

    try:
        app = HABApp.runtime.Runtime()
        register_signal_handler()

        # start workers
        try:
            asyncio.ensure_future(app.start(cfg_folder))
            HABApp.core.const.loop.run_forever()
        except asyncio.CancelledError:
            pass

    except HABApp.config.InvalidConfigException:
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
