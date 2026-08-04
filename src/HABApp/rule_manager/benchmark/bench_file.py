from asyncio import AbstractEventLoop
from pathlib import Path
from typing import override

import HABApp
from HABApp.core.internals import EventBus, ExecutorFactory, ItemRegistry
from HABApp.mqtt import MqttAsyncInterface, MqttInterface
from HABApp.openhab.connection.handler import OpenHabAsyncInterface, OpenHabSyncInterface
from HABApp.rule.interfaces.http_client import HABAppHttpClient
from HABApp.rule.rule_hook import HABAppRuleHook
from HABApp.rule_manager import RuleFile, RuleManager
from HABApp.rule_manager.benchmark.bench_habapp import HABAppBenchRule
from HABApp.rule_manager.benchmark.bench_mqtt import MqttBenchRule
from HABApp.rule_manager.benchmark.bench_oh import OpenhabBenchRule


class BenchFile(RuleFile):
    def __init__(self, rule_manager: RuleManager) -> None:
        super().__init__(rule_manager, 'BenchmarkFile', path=Path('BenchmarkFile'))

    @override
    def create_rules(self, created_rules: list,  # noqa: PLR0913
                     loop: AbstractEventLoop, async_http_client: HABAppHttpClient,
                     item_registry: ItemRegistry, event_bus: EventBus,
                     executor_factory: ExecutorFactory,
                     mqtt_interface_sync: MqttInterface, mqtt_interface_async: MqttAsyncInterface,
                     oh_interface_sync: OpenHabSyncInterface, oh_interface_async: OpenHabAsyncInterface
                     ) -> None:
        rule_hook = HABAppRuleHook(
            created_rules.append, self.suggest_rule_name,
            self.rule_manager, self, loop=loop, async_http_client=async_http_client,
            item_registry=item_registry, event_bus=event_bus, executor_factory=executor_factory,
            mqtt_interface_sync=mqtt_interface_sync, mqtt_interface_async=mqtt_interface_async,
            oh_interface_sync=oh_interface_sync, oh_interface_async=oh_interface_async
        )
        rule_hook.in_dict(globals())

        rule_ha = rule = HABAppBenchRule()
        if HABApp.CONFIG.mqtt.connection.host:
            rule = rule.link_rule(MqttBenchRule())
        if HABApp.CONFIG.openhab.connection.url:
            rule = rule.link_rule(OpenhabBenchRule())

        rule_ha.run.at(5, rule_ha.do_bench_start)
