import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

from openhab_runner.const import setup_logging
from openhab_runner.models import CONFIG
from openhab_runner.run_tasks import TaskHelper, run_openhab
from openhab_runner.select_oh import setup_openhab_runner
from openhab_runner.sync import sync_data


def parse_args(args: Sequence[str] | None = None) -> Path:

    parser = argparse.ArgumentParser(description='Start openHAB runner')
    parser.add_argument(
        '-c',
        '--config',
        help='Path to configuration file',
        default=None
    )

    args = parser.parse_args(args)

    if (cmd_cfg := args.config) is not None:
        cfg = Path(cmd_cfg).resolve()
    else:
        run_folder = Path(__file__).parent.parent.with_name('run')
        cfg = run_folder / 'oh_runner.yaml'

    if cfg.is_dir():
        msg = f'File {cfg} is a directory'
        raise ValueError(msg)

    if not (folder := cfg.parent).is_dir():
        msg = f'Folder {folder} does not exist!'
        raise FileNotFoundError(msg)

    return cfg


def main() -> None:
    setup_logging()
    cfg_path = parse_args()
    CONFIG.load_config_file(cfg_path, expansion=False)
    logging.getLogger().setLevel(CONFIG.logging.level)

    runner = setup_openhab_runner()

    # copy all files
    sync_data(runner.sync, test=CONFIG.test_sync)

    # start tasks
    with TaskHelper() as tasks:
        tasks.run_tasks(runner.tasks.on_start)

        # run openhab
        run_openhab(runner)

        # Tasks after openhab
        tasks.stop_tasks()
        tasks.run_tasks(runner.tasks.on_close)


if __name__ == '__main__':
    main()
