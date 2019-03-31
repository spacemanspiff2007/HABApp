import argparse
import asyncio
import concurrent
import os
import logging, traceback, typing
import signal
import sys
from pathlib import Path

import HABApp

parser = argparse.ArgumentParser(description='Start HABApp')
parser.add_argument(
    '-c',
    '--config',
    help='Path to configuration folder (where the config.yml is located)"',
    default=None
)
args = parser.parse_args()
if args.config is not None:
    args.config = Path(args.config).resolve()


def find_config_folder() -> Path:
    check_path = [
        Path(os.getcwd()) / 'HABApp',                          # current working dir
        Path(os.environ.get('VIRTUAL_ENV', '')) / 'HABApp',    # Virtual env dir
        Path.home() / 'HABApp',                                #
    ]
    if args.config is not None:
        check_path = [args.config]

    for p in check_path:
        p = p.resolve()
        if not p.is_dir():
            continue

        f = p / 'config.yml'
        if f.is_file():
            return p

    # we have specified a folder, if the config does not exist we will create it
    if args.config is not None and args.config.is_dir():
        return args.config

    # we have nothing found and nothing specified -> exit
    print('Config file "config.yml" not found!')
    print('Checked folders:\n - ' + '\n - '.join(str(k) for k in check_path if str(k) != 'HABApp'))
    print('Please create file or specify a folder with the "-c" arg switch.')
    sys.exit(1)



def main() -> typing.Union[int, str]:
    loop = None
    log = logging.getLogger('HABApp')

    try:
        loop = asyncio.get_event_loop()
        loop.set_debug(True)

        app = HABApp.Runtime(find_config_folder())

        def shutdown_handler(sig, frame):
            print('Shutting down ...')
            app.shutdown.request_shutdown()

        # register shutdown helper
        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)

        # start workers
        try:
            loop.run_until_complete(app.get_async())
        except concurrent.futures._base.CancelledError:
            pass
    except Exception as e:
        for line in traceback.format_exc().splitlines():
            log.error(line)
            print(e)
        return str(e)
    finally:
        loop.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
