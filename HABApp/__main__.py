import argparse
import asyncio
import logging
import os
import signal
import sys
import traceback
import typing
from pathlib import Path

import HABApp


def find_config_folder(arg_config_path: typing.Optional[Path]) -> Path:

    check_path = [
        Path(os.getcwd()) / 'HABApp',                          # current working dir
        Path(os.environ.get('VIRTUAL_ENV', '')) / 'HABApp',    # Virtual env dir
        Path.home() / 'HABApp',                                # User home
    ]
    check_path = [ k for k in check_path if k if str(k) != 'HABApp']

    # override automatic check if we have specified something
    if arg_config_path is not None:
        check_path = [arg_config_path]

    for config_folder in check_path:
        config_folder = config_folder.resolve()
        if not config_folder.is_dir():
            continue

        config_file = config_folder / 'config.yml'
        if config_file.is_file():
            return config_folder

    # we have specified a folder, but the config does not exist so we will create it
    if arg_config_path is not None and arg_config_path.is_dir():
        return arg_config_path

    # we have nothing found and nothing specified -> exit
    print('Config file "config.yml" not found!')
    print('Checked folders:\n - ' + '\n - '.join(str(k) for k in check_path))
    print('Please create file or specify a folder with the "-c" arg switch.')
    sys.exit(1)


def get_command_line_args():
    parser = argparse.ArgumentParser(description='Start HABApp')
    parser.add_argument(
        '-c',
        '--config',
        help='Path to configuration folder (where the config.yml is located)"',
        default=None
    )
    parser.add_argument('--NoMQTTConnectionErrors', required=False, action='store_true')
    return parser.parse_args()


def main() -> typing.Union[int, str]:

    args = get_command_line_args()
    if args.config is not None:
        args.config = Path(args.config).resolve()
    if args.NoMQTTConnectionErrors is True:
        HABApp.mqtt.MqttInterface._RAISE_CONNECTION_ERRORS = False

    loop = None
    log = logging.getLogger('HABApp')

    # if installed we use uvloop because it seems to be much faster (untested)
    try:
        import uvloop
        uvloop.install()
        print('Using uvloop')
    except ModuleNotFoundError:
        pass

    try:
        loop = asyncio.get_event_loop()

        loop.set_debug(True)
        loop.slow_callback_duration = 0.02

        app = HABApp.Runtime(config_folder=find_config_folder(args.config))

        def shutdown_handler(sig, frame):
            print('Shutting down ...')
            app.shutdown.request_shutdown()

        # register shutdown helper
        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)

        # start workers
        try:
            loop.run_until_complete(app.get_async())
        except asyncio.CancelledError:
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
