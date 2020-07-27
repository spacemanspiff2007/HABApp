from pathlib import Path
from typing import Set, Dict

import HABApp
from HABApp.openhab.connection_handler.func_async import async_get_item, async_get_channel_links, \
    async_set_habapp_metadata, async_create_item, async_remove_item, async_create_channel_link, async_get_items, \
    async_remove_channel_link
from ._log import log_item as log
from .cfg_validator import UserItem


def _filter_items(i):
    if not i.get('editable', False):
        return False

    meta = i.get('metadata', {})
    if 'HABApp' not in meta:
        return False

    if meta['HABApp'].get('config', {}).get('created_by') != 'thing_plugin':
        return False
    return True


async def cleanup_items(keep_items: Set[str]):
    all_items = await async_get_items(include_habapp_meta=True)

    to_delete = []
    for cfg in filter(_filter_items, all_items):
        name = cfg['name']
        if name not in keep_items:
            to_delete.append(name)

    if not to_delete:
        return None
    all_links = await async_get_channel_links()

    for item in to_delete:
        # first we remove the channel links
        for link_cfg in filter(lambda x: x['itemName'] == item, all_links):
            c_uid = link_cfg['channelUID']
            log.debug(f'Removing link from {c_uid} to {item}')
            await async_remove_channel_link(c_uid, item)
        # then the item
        log.info(f'Removing obsolete item {item}')
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
        existing = await async_get_item(name, include_habapp_meta=True)

        # we only modify items we created
        if existing.get('metadata', {}).get('HABApp', {}).get('config', {}).get('created_by') != 'thing_plugin':
            log.warning(f'Skipping item {name} because it does already exist and was not created by the plugin!')
            return False

        # check if the properties are already correct
        item_ok = True
        for k, v in item.get_oh_cfg().items():
            if v != existing.get(k, ''):
                item_ok = False

        if item_ok:
            log.debug(f'Item {name} is already correct!')
            return True
    except HABApp.openhab.exceptions.ItemNotFoundError:
        pass

    log.info(f'Creating item: {item.type} {name} "{item.label}"')
    tmp = item.get_oh_cfg()
    tmp['item_type'] = tmp.pop('type')
    await async_create_item(**tmp)

    # set metadata so we can automatically delete them again
    if await async_set_habapp_metadata(name, {'created_by': 'thing_plugin'}):
        # if we don't have a link we are done
        if item.link is None:
            return True

        # create link between item and channel
        if await async_create_channel_link(item.link, name):
            return True
        else:
            log.error(f'Could not link item {name} to channel {item.link}!')

    # couldn't set metadata -> remove again!
    await async_remove_item(name)
    return False


def create_items_file(path: Path, items: Dict[str, UserItem]):

    field_fmt = {
        'type': '{}',
        'name': '{}',
        'label': '"{}"',
        'icon': '<{}>',
        'groups': '({})',
        'tags': '[{}]',
        'link': '{{channel = "{}"}}'
    }

    values = []
    for item in items.values():
        new = {}
        for k, format in field_fmt.items():
            val = item.__dict__[k]
            if isinstance(val, list):
                val = ', '.join(val)

            new[k] = format.format(val) if val else ''

        values.append(new)

    # if we have no items we don't create the file
    if not values:
        return None

    f_dict = {}
    for k in field_fmt.keys():
        width = max(map(len, map(lambda x: x[k], values)), default=0)
        # indent to multiples of 4, if the entries are missing do not indent
        if width:
            for _ in range(4):
                width += 1
                if not width % 4:
                    break
        else:
            # set with to 1 because format crashes with with=0
            width = 1

        f_dict[f'w_{k}'] = width

    fmt_str = ' '.join(f'{{{k}:{{w_{k}}}s}}' for k in field_fmt.keys()) + '\n'

    with path.open(mode='w', encoding='utf-8') as file:
        for v in values:
            file.write(fmt_str.format(**f_dict, **v))
