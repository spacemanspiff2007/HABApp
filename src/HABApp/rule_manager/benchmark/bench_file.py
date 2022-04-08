from pathlib import Path

import HABApp
from HABApp.rule.rule_hook import HABAppRuleHook
from HABApp.rule_manager import RuleFile
from .bench_habapp import HABAppBenchRule
from .bench_mqtt import MqttBenchRule
from .bench_oh import OpenhabBenchRule


class BenchFile(RuleFile):
    def __init__(self, rule_manager):
        super().__init__(rule_manager, 'BenchmarkFile', path=Path('BenchmarkFile'))

    def create_rules(self, created_rules: list):
        HABAppRuleHook.in_dict(globals(), created_rules.append, self.suggest_rule_name, self.rule_manager.runtime, self)

        rule_ha = rule = HABAppBenchRule()
        if HABApp.CONFIG.mqtt.connection.host:
            rule = rule.link_rule(MqttBenchRule())
        if HABApp.CONFIG.openhab.connection.url:
            rule = rule.link_rule(OpenhabBenchRule())

        rule_ha.run.at(5, rule_ha.do_bench_start)
