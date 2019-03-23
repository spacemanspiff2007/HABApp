import collections
import logging
import runpy
import traceback
import typing
from pathlib import Path

if typing.TYPE_CHECKING:
    import HABApp

log = logging.getLogger(f'HABApp.Rules')


class RuleFile:
    def __init__(self, rule_manager, path: Path):
        from .rule_manager import RuleManager

        assert isinstance(rule_manager, RuleManager)
        self.rule_manager = rule_manager

        self.path = path

        self.rules = {}

        self.class_ctr = collections.defaultdict(lambda : 1)

    def suggest_rule_name(self, obj) -> str:

        # if there is already a name set we make no suggestion
        if getattr(obj, 'rule_name', '') != '':
            return obj.rule_name.replace('ü', 'ue').replace('ö', 'oe').replace('ä', 'ae')

        # create unique name
        name = f'{str(type(obj))[19:-2]:s}'
        found = self.class_ctr[name]
        self.class_ctr[name] += 1

        return f'{name:s}.{found:d}' if found > 1 else f'{name:s}'

    def iterrules(self):
        for rule in self.rules.values():
            yield rule

    def check_all_rules(self):
        for rule in self.rules.values():  # type: HABApp.Rule
            rule._check_rule()

    def unload(self):

        # If we don't have any rules we can not unload
        if not self.rules:
            return None

        # unload all registered callbacks
        for rule in self.rules.values():  # type: HABApp.Rule
            rule._cleanup()

        log.debug(f'File {self.path} successfully unloaded!')
        return None

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
            for rule in created_rules:
                # ensure that we have a rule name
                rule.rule_name = self.suggest_rule_name(rule)

                # rule name must be unique for every file
                if rule.rule_name in self.rules:
                    raise ValueError(f'Rule name must be unique!\n"{rule.rule_name}" is already used!')

                self.rules[rule.rule_name] = rule
                log.info(f'Added rule "{rule.rule_name}" from {self.path.name}')

        return None
