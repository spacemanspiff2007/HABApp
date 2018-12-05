import asyncio, os, sys
import argparse
import signal, concurrent
from pathlib import Path

import HABApp

parser = argparse.ArgumentParser(description='Start HABApp')
parser.add_argument("-c", "--config", help='Path to configuration folder (where the config.yml is located)"', default=None)
args = parser.parse_args()

def find_config_folder() -> Path:
    check_path = [
        Path(os.getcwd()) / 'HABApp',                          # current working dir
        Path(os.environ.get('VIRTUAL_ENV', '')) / 'HABApp',    # Virtual env dir
        Path.home() / 'HABApp',                                #
    ]
    if args.config is not None:
        check_path = [Path(args.config)]

    for p in check_path:
        p = p.resolve()
        if not p.is_dir():
            continue

        f = p / 'config.yml'
        if f.is_file():
            return p

    # we have nothing found -> exit
    print('Config file "config.yml" not found!')
    print('Checked folders:\n - ' + '\n - '.join(str(k) for k in check_path if str(k) != 'HABApp'))
    print('Please create file or specify a different folder with the "-c" arg switch.')
    sys.exit(1)

try:
    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    app = HABApp.Runtime(find_config_folder())


    def shutdown_handler(sig, frame):
        print('Shutting down ...')
        app.shutdown.request()

    # register shutdown helper
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # start workers
    try:
        loop.run_until_complete(app.get_async())
    except concurrent.futures._base.CancelledError:
        pass
except Exception as e:
    raise e
finally:
    loop.close()
