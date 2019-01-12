import collections
import logging
import runpy
import traceback
from pathlib import Path

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
        try:
            runpy.run_path(self.path, init_globals={
                '__HABAPP__RUNTIME__': self.rule_manager.runtime,
                '__HABAPP__RULE_FILE__': self,
                '__HABAPP__RULES' : created_rules
            })
        except Exception as e:
            log.error(f"Could not load {self.path}: {e}!")
            for l in traceback.format_exc().splitlines()[-5:]:
                log.error(l)

        len_found = len(created_rules)
        if not len_found:
            log.warning(f'Found no instances of HABApp.Rule in {str(self.path)}')
        else:
            ctr = collections.defaultdict(lambda : 1)
            for rule in created_rules:
                rule_name = rule.rule_name.replace('ü', 'ue').replace('ö', 'oe').replace('ä', 'ae')
                if not rule_name:
                    # create unique name
                    __class_name = f'{str(type(rule))[19:-2]:s}'
                    __classes_found = ctr[__class_name]
                    rule_name = f'{__class_name:s}.{__classes_found}' if __classes_found > 1 else f'{__class_name:s}'
                    ctr[__class_name] += 1

                # rule name must be unique for every file
                if rule_name in self.rules:
                    raise ValueError(f'Rule name must be unique!\n"{rule_name}" is already used!')

                self.rules[rule_name] = rule
                log.info(f'Added rule "{rule_name}" from {self.path.name}')

        return None
