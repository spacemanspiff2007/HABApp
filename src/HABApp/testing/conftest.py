# ruff: noqa: PLR0913, S101

import os
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from types import ModuleType
from typing import Any, Final, Literal
from unittest.mock import Mock

import eascheduler
import pytest
from easyconfig.yaml import yaml_safe as _yaml_safe
from whenever import Instant
from whenever import patch_current_time as _patch_current_time
from whenever._utils import _TimePatch

import HABApp.rule.rule as rule_module
from HABApp.config import ApplicationConfig
from HABApp.config.models.mqtt import MqttConfig
from HABApp.core.internals import EventBus, ExecutorFactory, ItemRegistry
from HABApp.core.items.base_item_times_data import ItemTimesBackup
from HABApp.core.lib import DebouncedCallRegistry
from HABApp.core.lib.asyncio import AsyncioProvider
from HABApp.core.provider import HABAPP_PROVIDER, HabAppObjProvider
from HABApp.mqtt import MqttAsyncInterface, MqttInterface
from HABApp.mqtt.connection.messages import MessagesHandler
from HABApp.mqtt.connection.messages import MessagesHandler as MqttMessagesHandler
from HABApp.openhab.connection.handler import OpenHabAsyncInterface, OpenHabSyncInterface
from HABApp.openhab.item_registry_handler import OhItemRegistryHandler
from HABApp.rule.rule_hook import HABAppRuleHook
from HABApp.testing.executor import TestingExecutorFactory
from HABApp.testing.inspect_habapp import find_in_modules
from HABApp.testing.items import TestingItemFactory, TestingItems
from HABApp.testing.mqtt import MqttLoopbackQueue
from HABApp.testing.oh import OhWebsocketLoopbackQueue
from HABApp.testing.rules import RuleRegistry
from HABApp.testing.scheduler import TestingScheduler, get_holiday, get_location
from HABApp.testing.time import AsyncioTestingProvider, PatchedTimeHelper, TestingStartTimeOptions, UserTimeControl


# Environment variable names which control testing
_ENV_PATH_TO_CONFIG: Final = 'HABAPP_TESTING__HABAPP_CONFIG'


@pytest.fixture(scope='session')
def habapp_config() -> ApplicationConfig | None:

    if not (env_value := os.environ.get(_ENV_PATH_TO_CONFIG)):
        return None

    path = Path(env_value)

    if not path.is_file():
        pytest.fail(reason=f'HABApp config does not exist: {path}')

    with path.open('r', encoding='utf-8') as file:
        cfg: dict[str, Any] = _yaml_safe.load(file)

    return ApplicationConfig.model_validate(cfg)


@pytest.fixture(scope='session')
def set_scheduler_config(habapp_config: ApplicationConfig | None) -> Literal['set_scheduler_config']:
    lat, long, elev = get_location(habapp_config)
    eascheduler.set_location(lat, long, elev)

    country, subdivision = get_holiday(habapp_config)
    eascheduler.setup_holidays(country, subdivision or None)

    return 'set_scheduler_config'


@pytest.fixture
def testing_start_time() -> TestingStartTimeOptions:
    return TestingStartTimeOptions(start=Instant.now().round('hour', mode='floor'), keep_ticking=False)


@pytest.fixture
def patch_current_time(testing_start_time: TestingStartTimeOptions) -> Generator[_TimePatch, None, None]:
    with _patch_current_time(testing_start_time.start, keep_ticking=testing_start_time.keep_ticking) as p:
        yield p


@pytest.fixture
def patched_time_helper(patch_current_time: _TimePatch) -> PatchedTimeHelper:
    return PatchedTimeHelper(patch_current_time)


@pytest.fixture
async def asyncio_provider(patched_time_helper: PatchedTimeHelper) -> AsyncGenerator[AsyncioTestingProvider, Any]:

    asyncio: Final = AsyncioTestingProvider(patched_time_helper)

    yield asyncio

    for t in asyncio._tasks:
        t.cancel()
    await asyncio.wait_for_tasks()


@pytest.fixture
def time_control(asyncio_provider: AsyncioTestingProvider) -> UserTimeControl:
    return UserTimeControl(asyncio_provider)


@pytest.fixture
def item_registry() -> ItemRegistry:
    return ItemRegistry()


@pytest.fixture
def event_bus() -> EventBus:
    return EventBus()


@pytest.fixture
def item_times_backup() -> ItemTimesBackup:
    return Mock(ItemTimesBackup)


@pytest.fixture(autouse=True)
def testing_scheduler(monkeypatch: pytest.MonkeyPatch,
                      asyncio_provider: AsyncioTestingProvider) -> Generator[TestingScheduler, Any, None]:

    scheduler: Final = TestingScheduler(asyncio_provider)

    def func(event_loop: Any, enabled: Any = None) -> TestingScheduler:
        return scheduler

    monkeypatch.setattr('HABApp.rule.scheduler.job_builder.AsyncHABAppScheduler', func)

    yield scheduler

    scheduler.remove_all()


@pytest.fixture(scope='session')
def habapp_provider_modules() -> tuple[tuple[ModuleType, str, Any], ...]:
    return tuple(find_in_modules(lambda x: x is HABAPP_PROVIDER))


@pytest.fixture
def debounced_call_registry(asyncio_provider: AsyncioTestingProvider) -> DebouncedCallRegistry:
    return DebouncedCallRegistry(asyncio_provider)


@pytest.fixture(autouse=True)
async def habapp_provider(  # noqa: PLR0913
        monkeypatch: pytest.MonkeyPatch, habapp_provider_modules: tuple[tuple[ModuleType, str, Any], ...],
        item_registry: ItemRegistry, event_bus: EventBus, item_times_backup: ItemTimesBackup,
        asyncio_provider: AsyncioTestingProvider, debounced_call_registry: DebouncedCallRegistry,
        interface_mqtt: MqttInterface, testing_executor_factory: TestingExecutorFactory
) -> AsyncGenerator[HabAppObjProvider, Any]:

    provider: Final = HabAppObjProvider()

    for module, name, _ in habapp_provider_modules:
        monkeypatch.setattr(module, name, provider)

    provider.add_object(item_registry, ItemRegistry)
    provider.add_object(event_bus, EventBus)
    provider.add_object(item_times_backup, ItemTimesBackup)
    provider.add_object(asyncio_provider, AsyncioProvider)
    provider.add_object(debounced_call_registry, DebouncedCallRegistry)
    provider.add_object(interface_mqtt, MqttInterface)
    provider.add_object(testing_executor_factory, ExecutorFactory)

    async with provider:
        yield provider


@pytest.fixture
def rule_registry() -> RuleRegistry:
    return RuleRegistry()


@pytest.fixture
def testing_items() -> TestingItems:
    return TestingItems()


@pytest.fixture
def oh_item_registry_handler(item_registry: ItemRegistry) -> OhItemRegistryHandler:
    return OhItemRegistryHandler(item_registry)


@pytest.fixture
def interface_oh(interface_oh_async: OpenHabAsyncInterface) -> OpenHabSyncInterface:
    return OpenHabSyncInterface(interface_oh_async)


@pytest.fixture
def oh_ws_loopbackqueue(event_bus: EventBus, item_registry: ItemRegistry) -> OhWebsocketLoopbackQueue:
    return OhWebsocketLoopbackQueue(event_bus=event_bus, item_registry=item_registry)


@pytest.fixture
def interface_oh_async(oh_ws_loopbackqueue: OhWebsocketLoopbackQueue,
                       item_registry: ItemRegistry) -> OpenHabAsyncInterface:

    return OpenHabAsyncInterface(
        websocket_queue=oh_ws_loopbackqueue, http_queue=Mock(), client=Mock(), ir=item_registry
    )


@pytest.fixture
def mqtt_msg_handler(event_bus: EventBus, item_registry: ItemRegistry,
                     asyncio_provider: AsyncioTestingProvider) -> MessagesHandler:
    return MqttMessagesHandler(None, event_bus, item_registry, asyncio_provider)


@pytest.fixture
def mqtt_loopback_queue(mqtt_msg_handler: MessagesHandler) -> MqttLoopbackQueue:
    return MqttLoopbackQueue(mqtt_msg_handler)


@pytest.fixture
def interface_mqtt_async(habapp_config: ApplicationConfig | None,
                         mqtt_loopback_queue: MqttLoopbackQueue) -> MqttAsyncInterface:

    return MqttAsyncInterface(
        publish_queue=mqtt_loopback_queue, subscription_handler=Mock(),
        config=MqttConfig() if habapp_config is None else habapp_config.mqtt
    )


@pytest.fixture
def interface_mqtt(interface_mqtt_async: MqttAsyncInterface, mqtt_msg_handler: MessagesHandler) -> MqttInterface:
    i = MqttInterface(interface_mqtt_async)

    # noinspection PyFinal

    # we have to assign it here otherwise we have a cyclic dependency
    mqtt_msg_handler._interface = i

    return i


@pytest.fixture
def testing_item_factory(event_bus: EventBus, item_registry: ItemRegistry,
                         oh_item_registry_handler: OhItemRegistryHandler,
                         interface_oh: OpenHabSyncInterface, interface_mqtt: MqttInterface) -> TestingItemFactory:
    return TestingItemFactory(
        event_bus=event_bus, item_registry=item_registry,
        oh_registry_handler=oh_item_registry_handler, if_oh=interface_oh, if_mqtt=interface_mqtt
    )


@pytest.fixture(autouse=True)
async def create_testing_items(testing_items: TestingItems, testing_item_factory: TestingItemFactory,
                               habapp_provider: HabAppObjProvider) -> Literal['create_testing_items']:

    # noinspection PyProtectedMember
    await testing_item_factory.create_items(testing_items._items)

    return 'create_testing_items'


@pytest.fixture
async def testing_executor_factory(event_bus: EventBus) -> AsyncGenerator[TestingExecutorFactory, Any]:

    f: Final = TestingExecutorFactory(event_bus)

    yield f

    assert not f.errors


@pytest.fixture
async def rule_hook(
        monkeypatch: pytest.MonkeyPatch, item_registry: ItemRegistry,
        event_bus: EventBus, rule_registry: RuleRegistry,
        interface_oh: OpenHabSyncInterface, interface_oh_async: OpenHabAsyncInterface,
        interface_mqtt: MqttInterface, interface_mqtt_async: MqttAsyncInterface,
        testing_executor_factory: TestingExecutorFactory
) -> AsyncGenerator[HABAppRuleHook, Any]:

    # Patch the hook so we can instantiate the rules
    hook = HABAppRuleHook(
        rule_registry.register_rule,
        rule_registry.suggest_rule_name,
        Mock(),
        None,
        None,
        None,
        item_registry=item_registry,
        event_bus=event_bus,
        executor_factory=testing_executor_factory,
        oh_interface_sync=interface_oh,
        oh_interface_async=interface_oh_async,
        mqtt_interface_sync=interface_mqtt,
        mqtt_interface_async=interface_mqtt_async,
    )
    monkeypatch.setattr(rule_module, '_get_rule_hook', lambda: hook)

    yield hook

# ----------------------------------------------------------------------------------------------------------------------
# CodeGen
# ----------------------------------------------------------------------------------------------------------------------
# - all: { select: {include: '.*', exclude_foreign: True, exclude: '^_'}}

__all__ = (
    'asyncio_provider',
    'create_testing_items',
    'debounced_call_registry',
    'event_bus',
    'habapp_config',
    'habapp_provider',
    'habapp_provider_modules',
    'interface_mqtt',
    'interface_mqtt_async',
    'interface_oh',
    'interface_oh_async',
    'item_registry',
    'item_times_backup',
    'mqtt_loopback_queue',
    'mqtt_msg_handler',
    'oh_item_registry_handler',
    'oh_ws_loopbackqueue',
    'patch_current_time',
    'patched_time_helper',
    'rule_hook',
    'rule_registry',
    'set_scheduler_config',
    'testing_executor_factory',
    'testing_item_factory',
    'testing_items',
    'testing_scheduler',
    'testing_start_time',
    'time_control',
)
