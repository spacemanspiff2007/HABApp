from enum import Enum
from pathlib import Path
from typing import Literal

from easyconfig import AppConfigMixin, create_app_config
from pydantic import BaseModel as _BaseModel
from pydantic import ConfigDict


class BaseModel(_BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid', validate_assignment=True, validate_default=True)


class LogConfig(BaseModel):
    level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = 'DEBUG'


class TaskModel(BaseModel):
    name: str
    command: str
    args: list[str] | None = None
    env: dict[str, str] | None = None
    cwd: str | None = None
    timeout: int | float | None = None

    shell: bool = False
    wait: bool = True
    new_console: bool = False


class LifeCycleTaskModel(BaseModel):
    on_start: list[TaskModel] = []
    on_close: list[TaskModel] = []


class SyncOptionEnum(str, Enum):
    MERGE = 'MERGE'
    REMOVE_FILES_AND_FOLDERS = 'REMOVE_FILES_AND_FOLDERS'
    REMOVE_FILES = 'REMOVE_FILES'


class SyncConfig(BaseModel):
    src: str
    dst: str
    mode: Literal[*tuple(t for t in SyncOptionEnum)] = 'REMOVE_FILES'


class InstallationConfig(BaseModel):
    name: str
    path: str
    java: str

    sync: list[SyncConfig] = []
    tasks: LifeCycleTaskModel = LifeCycleTaskModel(on_start=[], on_close=[])


class ConfigFileModel(BaseModel, AppConfigMixin):
    logging: LogConfig = LogConfig()

    sync: list[SyncConfig] = []
    test_sync: bool
    tasks: LifeCycleTaskModel = LifeCycleTaskModel(on_start=[], on_close=[])

    installations: list[InstallationConfig] = []


CONFIG = create_app_config(ConfigFileModel(test_sync=True), ConfigFileModel(
    logging=LogConfig(level='DEBUG'),
    sync=[SyncConfig(src='./conf_testing/lib/openhab', dst='./my/openhab/installation')],
    test_sync=True,
    tasks=LifeCycleTaskModel(
        on_start=[TaskModel(name='start', command='start.sh')],
        on_close=[TaskModel(name='stop', command='stop.sh')]
    ),
    installations=[
        InstallationConfig(
            name='openhab 1.0',
            path='/path/to/openhab',
            java='/path/to/java'
        )
    ],

))


class RunFolderSyncConfig(BaseModel):
    src: Path
    dst: Path
    mode: SyncOptionEnum


class RunConfig(BaseModel):
    name: str
    java_path: Path
    openhab_task: TaskModel
    openhab_logs: Path
    sync: list[RunFolderSyncConfig]
    tasks: LifeCycleTaskModel
