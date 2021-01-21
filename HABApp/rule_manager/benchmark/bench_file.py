from pathlib import Path

import HABApp
from HABApp.rule_manager import RuleFile
from .bench_habapp import HABAppBenchRule
from .bench_oh import OpenhabBenchRule
from .bench_mqtt import MqttBenchRule


class BenchFile(RuleFile):
    def __init__(self, rule_manager):
        super().__init__(rule_manager, path=Path('BenchmarkFile'))

    def create_rules(self, created_rules: list):
        glob = globals()
        glob['__HABAPP__RUNTIME__'] = self.rule_manager.runtime
        glob['__HABAPP__RULE_FILE__'] = self
        glob['__HABAPP__RULES'] = created_rules

        rule_ha = rule = HABAppBenchRule()
        if HABApp.CONFIG.mqtt.connection.host:
            rule = rule.link_rule(MqttBenchRule())
        if HABApp.CONFIG.openhab.connection.host:
            rule = rule.link_rule(OpenhabBenchRule())

        rule_ha.run_in(5, rule_ha.do_bench_start)

        glob.pop('__HABAPP__RUNTIME__')
        glob.pop('__HABAPP__RULE_FILE__')
        glob.pop('__HABAPP__RULES')
