from typing import Set, Dict

import HABApp
from HABApp.openhab.connection.handler.func_async import async_set_habapp_metadata, async_create_item, \
    async_remove_item, async_create_link, async_get_items, \
    async_remove_link, async_remove_metadata, async_set_metadata, async_get_item_with_habapp_meta
from HABApp.openhab.definitions.rest import ItemResp
from HABApp.openhab.definitions.rest.habapp_data import HABAppThingPluginData, load_habapp_meta
from ._log import log_item as log
from .cfg_validator import UserItem


def _filter_items(i: ItemResp):
    if not i.editable:
        return False

    if 'HABApp' not in i.metadata:
        return False

    load_habapp_meta(i)
    if not isinstance(i.metadata['HABApp'], HABAppThingPluginData):
        return False
    return True


async def cleanup_items(keep_items: Set[str]):
    all_items = await async_get_items()

    to_delete: Dict[str, HABAppThingPluginData] = {}
    for cfg in filter(_filter_items, all_items):
        name = cfg.name
        if name not in keep_items:
            to_delete[name] = cfg['metadata']['HABApp']

    if not to_delete:
        return None

    for item, data in to_delete.items():
        assert isinstance(data, HABAppThingPluginData)
        await _remove_item(item, data)


async def _remove_item(item: str, data: HABAppThingPluginData):
    # remove created links
    if data.created_link is not None:
        log.debug(f'Removing link from {data.created_link} to {item}')
        await async_remove_link(item, data.created_link)

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
        habapp_data = existing_item.metadata['HABApp']

        # we only modify items we created
        if not isinstance(habapp_data, HABAppThingPluginData):
            log.warning(f'Skipping item {name} because it does already exist and was not created by the plugin!')
            return False

        # check if the item properties are already correct
        for k, v in item.get_oh_cfg().items():
            if v != getattr(existing_item, k, ''):
                existing_ok = False

    except HABApp.openhab.errors.ItemNotFoundError:
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
        existing_item = await async_get_item_with_habapp_meta(name)
    else:
        log.debug(f'Item {name} is already correct!')

    # check create link
    if item.link != habapp_data.created_link:
        # remove existing
        if habapp_data.created_link:
            log.debug(f'Removing link from {habapp_data.created_link} to {name}')
            await async_remove_link(name, habapp_data.created_link)

        # create new link
        log.debug(f'Creating link from {item.link} to {item.name}')
        if not await async_create_link(name, item.link):
            log.error(f'Creating link from {item.link} to {name} failed!')
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
            existing_cfg = existing_item.metadata.get(ns, {})
            if 'config' not in existing_cfg:
                existing_cfg['config'] = {}
            if existing_cfg == meta_cfg:
                log.debug(f'Metadata for {name} is already correct')
                continue

            m_val = meta_cfg['value']
            m_config = meta_cfg['config']
            log.debug(f'Adding metadata {ns} to {name}: {m_val} {m_config}')
            if await async_set_metadata(name, ns, m_val, m_config):
                habapp_data.created_ns.append(ns)
            else:
                log.error(f'Creating metadata for {name} failed!')
                await _remove_item(name, habapp_data)
                return False

        # save that we created metadata
        habapp_data.created_ns = list(item.metadata.keys())
        await async_set_habapp_metadata(name, habapp_data)

    return True
