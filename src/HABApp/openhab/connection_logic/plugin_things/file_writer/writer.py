import re
from pathlib import Path
from typing import Iterable, Optional, List, Dict

from HABApp.core.const.const import PYTHON_311
from HABApp.openhab.connection_logic.plugin_things.cfg_validator import UserItem
from .formatter import FormatterScope
from .formatter_builder import ValueFormatterBuilder, MultipleValueFormatterBuilder, ConstValueFormatterBuilder, \
    MetadataFormatter, LinkFormatter

if not PYTHON_311:
    from typing_extensions import Self
else:
    from typing import Self


FIELD_ORDER = (
    'type', 'name', 'label', 'icon', 'groups', 'tags', 'bracket_open', 'link', 'metadata', 'bracket_close'
)

RE_GROUP_NAMES = re.compile(r'([A-Za-z0-9-]+?)(?=[A-Z_ -])')


def brackets_needed(obj: UserItem):
    return obj.link or obj.metadata


class ItemsFileWriter:
    def __init__(self):
        self.items: List[UserItem] = []

    def add_item(self, obj) -> Self:
        self.items.append(obj)
        return self

    def add_items(self, objs: Iterable[UserItem]) -> Self:
        self.items.extend(objs)
        return self

    def group_items(self) -> List[List[UserItem]]:
        grouped_items: Dict[Optional[str], List[UserItem]] = {}
        not_grouped: List[UserItem] = []
        for item in self.items:
            if m := RE_GROUP_NAMES.match(item.name):
                grouped_items.setdefault(m.group(1), []).append(item)
            else:
                not_grouped.append(item)

        ret = []
        # sort alphabetical by key
        for key, values in sorted(grouped_items.items(), key=lambda x: x[0]):
            # if it's only one value it'll be not written in a block
            if len(values) <= 1:
                not_grouped.extend(values)
                continue

            ret.append(values)

        # single entry items get created last
        if not_grouped:
            ret.append(not_grouped)

        return ret

    def generate(self) -> str:
        groups = self.group_items()

        builder = {
            'type': ValueFormatterBuilder('type', '{:s}'),
            'name': ValueFormatterBuilder('name', '{:s}'),
            'label': ValueFormatterBuilder('label', '"{:s}"'),
            'icon': ValueFormatterBuilder('icon', '<{:s}>'),
            'groups': MultipleValueFormatterBuilder('groups', '{:s}', '({:s})'),
            'tags': MultipleValueFormatterBuilder('tags', '"{:s}"', '[{:s}]'),
            'bracket_open': ConstValueFormatterBuilder('{', condition=brackets_needed),
            'link': LinkFormatter(),
            'metadata': MetadataFormatter(),
            'bracket_close': ConstValueFormatterBuilder('}', condition=brackets_needed),
        }

        lines = []

        for group in groups:
            scope = FormatterScope(FIELD_ORDER, ('bracket_open', 'bracket_close', 'metadata'))
            for item in group:
                scope.add({k: v.create_formatter(item) for k, v in builder.items()})

            lines.extend(scope.get_lines())
            lines.extend([''])

        return '\n'.join(lines)

    def create_file(self, file: Path):

        output = self.generate()

        # don't create empty files
        if not output:
            return False

        # only write changes
        if file.is_file():
            existing = file.read_text('utf-8')
            if existing == output:
                return False

        file.write_text(output, encoding='utf-8')
        return True
