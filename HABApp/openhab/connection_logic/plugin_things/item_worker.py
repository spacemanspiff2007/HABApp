from pathlib import Path
from typing import Set, Dict

import HABApp
from HABApp.openhab.connection_handler.func_async import async_set_habapp_metadata, async_create_item, \
    async_remove_item, async_create_channel_link, async_get_items, \
    async_remove_channel_link, async_remove_metadata, async_set_metadata, async_get_item_with_habapp_meta
from HABApp.openhab.definitions.rest.habapp_data import HABAppThingPluginData, load_habapp_meta
from ._log import log_item as log
from .cfg_validator import UserItem


def _filter_items(i):
    if not i.get('editable', False):
        return False

    if 'HABApp' not in i.setdefault('metadata', {}):
        return False

    load_habapp_meta(i)
    if not isinstance(i['metadata']['HABApp'], HABAppThingPluginData):
        return False
    return True


async def cleanup_items(keep_items: Set[str]):
    all_items = await async_get_items(include_habapp_meta=True)

    to_delete: Dict[str, HABAppThingPluginData] = {}
    for cfg in filter(_filter_items, all_items):
        name = cfg['name']
        if name not in keep_items:
            to_delete[name] = cfg['metadata']['HABApp']

    if not to_delete:
        return None

    for item, data in to_delete.items():
        assert isinstance(data, HABAppThingPluginData)
        await _remove_item(item, data)


async def _remove_item(item: str, data: HABAppThingPluginData):
    # remove created link
    if data.created_link is not None:
        log.debug(f'Removing link from {data.created_link} to {item}')
        await async_remove_channel_link(data.created_link, item)

    # remove created metadata
    for ns in data.created_ns:
        log.debug(f'Removing metadata {ns} from {item}')
        await async_remove_metadata(item, ns)

    # finally remove the item
    log.info(f'Removing item {item}')
    await async_remove_item(item)


async def create_item(item: UserItem, test: bool) -> bool:

    if test:
        _txt = str(item)
        if _txt.startswith('UserItem'):
            _txt = _txt[4:]
        log.info(f'Would create {_txt}')
        return False

    name = item.name

    try:
        existing_ok = True
        existing_item = await async_get_item_with_habapp_meta(name)
        habapp_data = existing_item['metadata']['HABApp']

        # we only modify items we created
        if not isinstance(habapp_data, HABAppThingPluginData):
            log.warning(f'Skipping item {name} because it does already exist and was not created by the plugin!')
            return False

        # check if the item properties are already correct
        for k, v in item.get_oh_cfg().items():
            if v != existing_item.get(k, ''):
                existing_ok = False

    except HABApp.openhab.exceptions.ItemNotFoundError:
        existing_ok = True
        existing_item = None
        habapp_data = HABAppThingPluginData()

    # Update/Create item definition
    if existing_item is None or not existing_ok:
        log.info(f'{"Creating" if existing_item is None else "Updating"} item: {item.type} {name} "{item.label}"')
        tmp = item.get_oh_cfg()
        tmp['item_type'] = tmp.pop('type')
        if not await async_create_item(**tmp):
            log.error(f'Item operation failed for {tmp}!')
            return False
        await async_set_habapp_metadata(name, habapp_data)
    else:
        log.debug(f'Item {name} is already correct!')

    # check create link
    if item.link != habapp_data.created_link:
        # remove existing
        if habapp_data.created_link:
            log.debug(f'Removing link from {habapp_data.created_link} to {name}')
            await async_remove_channel_link(habapp_data.created_link, name)

        # create new link
        log.debug(f'Creating link from {item.link} to {item.name}')
        if not await async_create_channel_link(item.link, name):
            log.error(f'Creating link failed!')
            await _remove_item(name, habapp_data)
            return False

        # save that we created a link
        habapp_data.created_link = item.link
        await async_set_habapp_metadata(name, habapp_data)
    else:
        log.debug(f'Link to {name} is already correct')

    # check create metadata
    if item.metadata or habapp_data.created_ns:
        # remove obsolete
        for ns in set(habapp_data.created_ns) - set(item.metadata.keys()):
            log.debug(f'Removing metadata {ns} from {name}')
            await async_remove_metadata(name, ns)

        # create new
        for ns, meta_cfg in item.metadata.items():
            m_val = meta_cfg['value']
            m_config = meta_cfg['config']
            log.debug(f'Adding metadata {ns} to {name}: {m_val} {m_config}')
            if await async_set_metadata(name, ns, m_val, m_config):
                habapp_data.created_ns.append(ns)
            else:
                log.error(f'Creating metadata failed!')
                await _remove_item(name, habapp_data)
                return False

        # save that we created metadata
        habapp_data.created_ns = list(item.metadata.keys())
        await async_set_habapp_metadata(name, habapp_data)

    return True


def create_items_file(path: Path, items: Dict[str, UserItem]):

    field_fmt = {
        'type': '{}',
        'name': '{}',
        'label': '"{}"',
        'icon': '<{}>',
        'groups': '({})',
        'tags': '[{}]',
        'bracket_open': '',
        'link': 'channel = "{}"',
        'metadata': '',
        'bracket_close': '',
    }

    values = []
    for item in items.values():
        new = {}
        for k, format in field_fmt.items():
            if k in ('bracket_open', 'metadata', 'bracket_close'):
                continue
            val = item.__dict__[k]
            if isinstance(val, list):
                val = ', '.join(val)

            new[k] = format.format(val) if val else ''

        if item.link or item.metadata:
            new['bracket_open'] = '{'
            new['bracket_close'] = '}'

        if item.metadata:
            __m = []
            for k, __meta in item.metadata.items():
                __val = __meta['value']
                __cfg = __meta['config']

                _str = f'{k}={__val}' if not isinstance(__val, str) else f'{k}="{__val}"'
                if __cfg:
                    __conf_strs = []
                    for _k, _v in __cfg.items():
                        __conf_strs.append(f'{_k}={_v}' if not isinstance(_v, str) else f'{_k}="{_v}"')
                    _str += f' [{", ".join(__conf_strs)}]'
                __m.append(_str)

            # link needs the "," so we indent properly
            if item.link:
                new['link'] += ', '
            # metadata
            new['metadata'] = ', '.join(__m)

        values.append(new)

    # if we have no items we don't create the file
    if not values:
        return None

    f_dict = {}
    for k in field_fmt.keys():
        width = 1

        if k not in ('bracket_open', 'metadata', 'bracket_close'):
            width = max(map(len, map(lambda x: x[k], values)), default=0)
            # indent to multiples of 4, if the entries are missing do not indent
            if width:
                for _ in range(4):
                    width += 1
                    if not width % 4:
                        break

        # set with to min 1 because format crashes with with=0
        f_dict[f'w_{k}'] = max(1, width)

    fmt_str = ' '.join(f'{{{k}:{{w_{k}}}s}}' for k in field_fmt.keys()) + '\n'

    with path.open(mode='w', encoding='utf-8') as file:
        for v in values:
            file.write(fmt_str.format(**f_dict, **v))
