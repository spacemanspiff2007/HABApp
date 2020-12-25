import itertools
from typing import List

from HABApp.core.logger import HABAppError
from HABApp.openhab.definitions.helpers.log_table import Table
from ._log import log_cfg as log
from .thing_config import ThingConfigChanger


def show_config_overview(cfgs: List[ThingConfigChanger], all_params):
    t = Table(heading='Current configuration')
    c_p = t.add_column('Parameter')
    c_s = [t.add_column(c.uid, alias=':'.join(c.uid.split(':')[-2:]) if ':' in c.uid else None) for c in cfgs]

    for p in itertools.chain(
            sorted(filter(lambda x: isinstance(x, int), all_params)),
            sorted(filter(lambda x: not isinstance(x, int), all_params))):
        c_p.add(str(p))
        for col, cfg in zip(c_s, cfgs):
            v = cfg.get(p, '')
            col.add(str(v))
    for line in t.get_lines():
        log.info(line)


async def update_thing_cfg(target_cfg, things, test: bool):

    cfgs = [ThingConfigChanger.from_dict(k['UID'], k.get('configuration', {})) for k in things]
    cur_vals = tuple(k.get_dict(filter=True) for k in cfgs)
    all_params = set()
    for k in cur_vals:
        all_params.update(k.keys())

    # Show overview
    if test:
        show_config_overview(cfgs, all_params)

    errs = HABAppError(log)
    skip_cfg = set()
    for param, value in target_cfg.items():
        for c in cfgs:
            try:
                c[param] = value
            except Exception as e:
                errs.add_exception(e)
                skip_cfg.add(c)

    if errs:
        errs.dump()
        if not test:
            show_config_overview(cfgs, all_params)

    # update the thing configs. If nothing has changed this will do nothing
    for c in cfgs:
        # do not create partially correct configs
        if c in skip_cfg:
            log.warning(f'Skip configuration for {c.uid} because of errors!')
            continue

        if test:
            if c.new:
                log.info(f'Would set {c.get_dict(True, True)} for {c.uid}')
            else:
                log.info(f'Nothing changed for {c.uid}')
        else:
            await c.update_thing_cfg()

    return None
