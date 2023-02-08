from typing import Final, Iterable, List, Dict, TypeVar

from HABApp.core.const.const import PYTHON_311

if not PYTHON_311:
    from typing_extensions import Self
else:
    from typing import Self


class ValueFormatter:
    def __init__(self, value: str):
        self.value: Final = value

    def len(self):
        return len(self.value)

    def format(self, width: int) -> str:
        return f'{self.value:<{width}s}'


class EmptyFormatter(ValueFormatter):
    def __init__(self):
        super().__init__('')


TYPE_FORMATTER = TypeVar('TYPE_FORMATTER', bound=ValueFormatter)


class FormatterScope:
    def __init__(self, field_names: Iterable[str],
                 skip_alignment: Iterable[str] = (), min_width: Dict[str, int] = {}):
        self.lines: List[Dict[str, TYPE_FORMATTER]] = []
        self.keys: Final = tuple(field_names)

        # alignment options
        self._align_skip: Final = skip_alignment
        self._align_min_width: Final = min_width

        assert set(skip_alignment).issubset(self.keys)

    def add(self, obj: Dict[str, TYPE_FORMATTER]) -> Self:
        assert set(obj.keys()).issubset(self.keys)
        self.lines.append(obj)
        return self

    def get_indent_dict(self, ) -> Dict[str, int]:
        columns: Dict[str, List[TYPE_FORMATTER]] = {key: [] for key in self.keys}
        for line_dict in self.lines:
            for key in self.keys:
                formatter = line_dict.get(key)
                if formatter is None:
                    formatter = EmptyFormatter()
                columns[key].append(formatter)

        column_width = {key: max(map(lambda x: x.len(), column)) for key, column in columns.items()}

        for key, width in column_width.items():
            # indent to multiples of 4, if the entries are missing do not indent
            if width and key not in self._align_skip:
                add = width % 4
                if not add:
                    add = 4
                width += add

            # option to set a minimum width
            width = max(width, self._align_min_width.get(key, 0))

            column_width[key] = width

        return column_width

    def get_lines(self) -> List[str]:
        if not self.lines:
            return []

        column_width = self.get_indent_dict()

        ret_lines = []
        for line_dict in self.lines:    # type: Dict[str, TYPE_FORMATTER]
            line_vals = []
            for key, value_formatter in line_dict.items():
                width = column_width.get(key, 0)
                if width == 0:
                    continue
                line_vals.append(value_formatter.format(width))
            ret_lines.append(''.join(line_vals).rstrip())

        return ret_lines
