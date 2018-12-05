import logging
from pathlib import Path
import runpy
import voluptuous

from HABApp.util.wrapper import WorkerRuleWrapper
import HABApp.rule

log = logging.getLogger(f'HABApp.Rules')


class RuleFile:
    def __init__(self, rule_manager, path: Path):
        from .rule_manager import RuleManager

        assert isinstance(rule_manager, RuleManager)
        self.rule_manager = rule_manager

        self.path = path

        self.rules = {}

    def iterrules(self):
        for rule in self.rules.values():
            yield rule

    def load(self):

        file_globals = runpy.run_path(self.path, init_globals={
            '__HABAPP__RUNTIME__': self.rule_manager.runtime,
            '__HABAPP__RULE_FILE__': self
        })

        # search for rule instances
        found_rules = {}
        for k, v in file_globals.items():
            if isinstance(v, HABApp.Rule):
                found_rules[k] = v

        len_found = len(found_rules)
        if not len_found:
            log.warning(f'Found no instances of HABApp.Rule in {str(self.path)}')
        else:
            for k, v in found_rules.items():
                rule_name = v.rule_name if v.rule_name else f'{str(type(v))[19:-2]:s}.{k:s}'
                self.rules[rule_name] = v
                log.info(f'Added rule "{rule_name}" from {self.path.name}')

        return None
