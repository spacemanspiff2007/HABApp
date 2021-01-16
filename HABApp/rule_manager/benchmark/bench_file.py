from pathlib import Path

from HABApp.rule_manager import RuleFile
from .bench_oh import OpenhabBenchRule


class BenchFile(RuleFile):
    def __init__(self, rule_manager):
        super().__init__(rule_manager, path=Path('BenchmarkFile'))

    def create_rules(self, created_rules: list):
        glob = globals()
        glob['__HABAPP__RUNTIME__'] = self.rule_manager.runtime
        glob['__HABAPP__RULE_FILE__'] = self
        glob['__HABAPP__RULES'] = created_rules

        r1 = OpenhabBenchRule()

        r1.run_in(5, r1.do_bench_start)

        glob.pop('__HABAPP__RUNTIME__')
        glob.pop('__HABAPP__RULE_FILE__')
        glob.pop('__HABAPP__RULES')
