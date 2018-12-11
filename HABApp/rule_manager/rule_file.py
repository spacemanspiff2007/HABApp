import logging
from pathlib import Path
import runpy
import collections

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

        created_rules = []
        file_globals = runpy.run_path(self.path, init_globals={
            '__HABAPP__RUNTIME__': self.rule_manager.runtime,
            '__HABAPP__RULE_FILE__': self,
            '__HABAPP__RULES' : created_rules
        })

        len_found = len(created_rules)
        if not len_found:
            log.warning(f'Found no instances of HABApp.Rule in {str(self.path)}')
        else:
            ctr = collections.defaultdict(lambda : 1)
            for rule in created_rules:
                rule_name = rule.rule_name
                if not rule_name:
                    # create unique name
                    __class_name = f'{str(type(rule))[19:-2]:s}'
                    rule_name = f'{__class_name:s}.{ctr[__class_name]}'
                    ctr[__class_name] += 1

                # rule name must be unique for every file
                if rule_name in self.rules:
                    raise ValueError(f'Rule name must be unique!\n"{rule_name}" is already used!')

                self.rules[rule_name] = rule
                log.info(f'Added rule "{rule_name}" from {self.path.name}')

        return None
