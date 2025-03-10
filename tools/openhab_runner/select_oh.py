import os
import sys
from itertools import chain
from pathlib import Path

from openhab_runner.models import (
    CONFIG,
    InstallationConfig,
    LifeCycleTaskModel,
    RunConfig,
    RunFolderSyncConfig,
    TaskModel,
)
from openhab_runner.placeholder import ConfigPlaceholder


def select_openhab_version() -> InstallationConfig:

    installations = CONFIG.installations

    print('Select openHAB installation (-1 to exit):')
    sel = {}
    for i, oh in enumerate(installations, start=1):
        print(f'{i: 3d}: {oh.name}')
        sel[str(i)] = oh

    while True:
        user_sel = input().strip().replace(' ', '').lower()
        ret = sel.get(user_sel)
        if ret is not None:
            print(f'Starting {ret.name}\n')
            return ret

        if user_sel == '-1':
            print('Exiting ...')
            sys.exit(0)

        print(f'No Entry found for {user_sel:s}! Please try again!')


def create_task(obj: TaskModel, placeholder: ConfigPlaceholder, env: dict[str, str]) -> TaskModel:
    ret = {}
    for name, value in obj.model_dump(exclude_unset=True).items():
        match value:
            case str():
                new_value = placeholder(value)
            case dict():
                new_value = {placeholder(k): placeholder(v) for k, v in value.items()}
            case list():
                new_value = [placeholder(v) for v in value]
            case int() | float() | bool() | None:
                new_value = value
            case _:
                msg = f'Unknown type {type(value)}'
                raise ValueError(msg)

        ret[name] = new_value

    # insert env variables
    env = env.copy()
    env.update(ret.get('env', {}))
    ret['env'] = env

    t = TaskModel(**ret)
    if not t.shell and not (p := Path(t.cmd)).is_file():
        msg = f'Command {p} not found!'
        raise FileNotFoundError(msg)

    if t.cwd and not (p := Path(t.cwd)):
        msg = f'Working directory {p} not found!'
        raise FileNotFoundError(msg)

    return TaskModel(**ret)


def build_run_config(config: InstallationConfig) -> RunConfig:
    placeholder = ConfigPlaceholder()
    oh_name = placeholder.add('openhab_name', config.name)

    placeholder.get_folder_path(config.path, add_as='openhab_root')
    placeholder.get_folder_path('%openhab_root%/conf', add_as='openhab_conf')
    placeholder.get_folder_path('%openhab_root%/userdata', add_as='openhab_userdata')
    placeholder.get_folder_path('%openhab_root%/runtime', add_as='openhab_runtime')

    # setup paths
    java_path = placeholder.get_folder_path(config.java, add_as='java_root')
    oh_path = placeholder.get_file_path('%openhab_root%/' + ('start.bat' if sys.platform == 'win32' else 'start.sh'))
    oh_logs = placeholder.get_folder_path('%openhab_userdata%/logs', add_as='openhab_logs')

    # setup sync
    sync: list[RunFolderSyncConfig] = [
        RunFolderSyncConfig(src=placeholder.get_folder_path(f.src), dst=placeholder.get_folder_path(f.dst), mode=f.mode)
        for f in chain(CONFIG.sync, config.sync)
    ]

    # setup tasks
    env_vars = dict(os.environ)
    env_vars['JAVA_HOME'] = str(java_path)
    env_vars['PATH'] = f'{java_path / "bin"}{os.pathsep:s}{env_vars["PATH"]:s}'

    tasks = LifeCycleTaskModel(
        on_start=[create_task(t, placeholder, env_vars) for t in chain(CONFIG.tasks.on_start, config.tasks.on_start)],
        on_close=[create_task(t, placeholder, env_vars) for t in chain(config.tasks.on_close, CONFIG.tasks.on_close)],
    )

    tasks.on_start.insert(
        0, create_task(
            TaskModel(name='java info', cmd='java.exe', args=['-version'], shell=True),
            placeholder, env_vars
        )
    )

    oh_task = create_task(
        TaskModel(
            name='openhab', cmd=str(oh_path), cwd='%openhab_root%', env=env_vars,
            wait=False, new_console=True
        ),
        placeholder, env_vars
    )

    return RunConfig(
        name=oh_name,
        java_path=java_path,
        openhab_task=oh_task,
        openhab_logs=oh_logs,
        sync=sync,
        tasks=tasks,
    )


def setup_openhab_runner() -> RunConfig:
    return build_run_config(select_openhab_version())
