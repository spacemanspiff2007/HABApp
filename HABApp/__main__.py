import argparse
import asyncio
import logging
import os
import signal
import sys
import time
import traceback
import typing
from pathlib import Path

import HABApp


def find_config_folder(arg_config_path: typing.Optional[Path]) -> Path:

    if arg_config_path is None:
        # Nothing is specified, we try to find the config automatically
        check_path = []
        try:
            working_dir = Path(os.getcwd())
            check_path.append( working_dir / 'HABApp')
            check_path.append( working_dir.with_name('HABApp'))
            check_path.append( working_dir.parent.with_name('HABApp'))
        except ValueError:
            # the ValueError gets raised if the working_dir or its parent is empty (e.g. c:\ or /)
            pass

        check_path.append(Path.home() / 'HABApp')   # User home

        # if we run in a venv check the venv, too
        v_env = os.environ.get('VIRTUAL_ENV', '')
        if v_env:
            check_path.append(Path(v_env) / 'HABApp')  # Virtual env dir
    else:
        # Override automatic config detection if something is specified through command line
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


def get_command_line_args(args=None):
    parser = argparse.ArgumentParser(description='Start HABApp')
    parser.add_argument(
        '-c',
        '--config',
        help='Path to configuration folder (where the config.yml is located)',
        default=None
    )
    parser.add_argument(
        '-s',
        '--sleep',
        help='Sleep time in seconds before starting HABApp',
        type=int,
        default=None
    )
    parser.add_argument(
        '--NoMQTTConnectionErrors', required=False, action='store_true',
        help='Suppress MQTT connection errors and only log them (for testing without a connected MQTT Broker)'
    )
    return parser.parse_args(args)


def main() -> typing.Union[int, str]:

    args = get_command_line_args()
    if args.sleep:
        args.sleep = max(0, args.sleep)
        print(f'Waiting {args.sleep:d} seconds before starting HABApp ...', end='')
        time.sleep(args.sleep)
        print(' done!')
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
        # otherwise creating a subprocess does not work on windows
        if sys.platform == "win32":
            # This is the default from 3.8 so we don't have to set it ourselfs
            if sys.version_info < (3, 8):
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        else:
            # Must be called once in the main thread so creating a subprocess works properly
            # https://docs.python.org/3/library/asyncio-subprocess.html#subprocess-and-threads
            asyncio.get_child_watcher()

        loop = asyncio.get_event_loop()

        loop.set_debug(True)
        loop.slow_callback_duration = 0.02

        app = HABApp.Runtime()
        app.load_config(config_folder=find_config_folder(args.config))

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
    except HABApp.config.InvalidConfigException:
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
