from pathlib import Path
from typing import Dict, List
import re

from .cfg_validator import UserItem


RE_GROUP_NAMES = re.compile(r'([A-Za-z0-9-]+?)(?=[A-Z_ -])')


def _get_item_val_dict(field_fmt: Dict[str, str], item: UserItem):
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
    else:
        new['bracket_open'] = ''
        new['bracket_close'] = ''

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
            new['link'] += ','
        # metadata
        new['metadata'] = ', '.join(__m)
    else:
        new['metadata'] = ''

    return new


def _get_fmt_str(field_fmt: Dict[str, str], vals: List[Dict[str, str]]) -> str:
    w_dict = {}
    for k in field_fmt.keys():
        #
        #     w_dict[k] = 0
        #     continue

        width = max(map(len, map(lambda x: x[k], vals)), default=0)
        # indent to multiples of 4, if the entries are missing do not indent
        if width and k not in ('bracket_open', 'bracket_close', 'metadata'):
            add = width % 4
            if not add:
                add = 4
            width += add
        w_dict[k] = width

    ret = ''
    for k in field_fmt.keys():
        w = w_dict[k]
        if not w:
            ret += f'{{{k}:s}}'  # format crashes with with=0 so this is a different format string
            continue
        else:
            ret += f'{{{k}:{w}s}}'
    return ret


def create_items_file(path: Path, items_dict: Dict[str, UserItem]):
    # if we don't have any items we don't create an empty file
    if not items_dict:
        return None

    field_fmt = {
        'type': '{}',
        'name': '{}',
        'label': '"{}"',
        'icon': '<{}>',
        'groups': '({})',
        'tags': '[{}]',
        'bracket_open': '',
        'link': 'channel = "{}"',
        'metadata': '{}',
        'bracket_close': '',
    }

    grouped_items = {None: []}
    for _name, _item in items_dict.items():
        m = RE_GROUP_NAMES.match(_name)
        grp = grouped_items.setdefault(m.group(1) if m is not None else None, [])
        grp.append(_get_item_val_dict(field_fmt, _item))

    # aggregate single entry items to a block
    _aggr = []
    for _name, _items in grouped_items.items():
        if len(_items) <= 1 and _name is not None:
            _aggr.append(_name)
    for _name in _aggr:
        grouped_items[None].extend(grouped_items[_name])
        grouped_items.pop(_name)

    # single entry items get created at the end of file
    if None in grouped_items:
        grouped_items[None] = grouped_items.pop(None)

    lines = []
    for _name, _item_vals in grouped_items.items():
        # skip empty items
        if not _item_vals:
            continue

        fmt = _get_fmt_str(field_fmt, _item_vals)

        for _val in _item_vals:
            _l = fmt.format(**_val)
            lines.append(_l.strip() + '\n')

        # newline aber each name block
        lines.append('\n')

    with path.open(mode='w', encoding='utf-8') as file:
        file.writelines(lines)
