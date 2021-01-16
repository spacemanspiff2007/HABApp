import argparse
import os
import sys
import time
import typing
from pathlib import Path

# Global var if we want to run the benchmark
DO_BENCH = False


def parse_args(passed_args=None) -> Path:
    global DO_BENCH

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
        '-b',
        '--benchmark',
        help='Do a Benchmark based on the current config',
        action='store_true'
    )
    args = parser.parse_args(passed_args)

    DO_BENCH = args.benchmark

    if args.sleep:
        args.sleep = max(0, args.sleep)
        print(f'Waiting {args.sleep:d} seconds before starting HABApp ...', end='')
        time.sleep(args.sleep)
        print(' done!')

    path = args.config
    if path is not None:
        path = Path(path).resolve()
    return find_config_folder(path)


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
        # in case the user specifies the config.yml we automatically switch to the parent folder
        if arg_config_path.name.lower() == 'config.yml' and arg_config_path.is_file():
            arg_config_path = arg_config_path.parent

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
