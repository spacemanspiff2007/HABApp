from collections import OrderedDict
from typing import Any


class Column:
    wrap: int = 80

    def __init__(self, name: str, align: str | None = None, alias: str | None = None, wrap: int | None = None) -> None:
        self.name: str = name
        self.alias: str | None = alias

        self.align: str | None = align
        if wrap is not None:
            self.wrap = wrap

        self.width: int = len(name) if alias is None else len(alias)
        self.entries: list[tuple[Any, ...]] = []

    def count_lines(self, pos: int) -> int:
        return len(self.entries[pos])

    def format_entry(self, pos: int, lines: int) -> list[str]:
        ret = []

        objs = self.entries[pos]
        size = len(objs)
        for i in range(lines):
            if i >= size:
                ret.append(self.width * ' ')
                continue
            val = objs[i]
            if isinstance(val, bool):
                val = str(val)
            f = f'{{:{""if self.align is None else self.align}{self.width:d}}}'
            ret.append(f.format(val))
        return ret

    def add(self, val) -> None:
        _res = []
        if isinstance(val, (list, set, tuple)):
            _len = 0
            _str = ''
            for obj in val:
                if _len >= self.wrap:
                    _len = 0
                    _res.append(_str)
                    _str = ''
                _str = f'{_str}, {obj}' if _str else f'{obj}'
                _len = len(_str)
            _res.append(_str)
        else:
            _res.append(val)

        for k in _res:
            self.width = max(self.width, len(str(k)))
        self.entries.append(tuple(_res))

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} name: {self.name}'


class Table:
    def __init__(self, heading: str = '') -> None:
        self.columns: dict[str, Column] = OrderedDict()
        self.heading: str = heading

    def add_column(self, name: str, align: str | None = None, alias: str | None = None,
                   wrap: int | None = None) -> Column:
        self.columns[name] = c = Column(name, align, alias, wrap)
        return c

    def add_dict(self, _in: dict) -> None:
        for k, col in self.columns.items():
            col.add(_in[k])

    def get_lines(self, sort_columns: list[str | Column] | None = None) -> list[str]:
        # check if all tables have the same length
        vals = list(self.columns.values())
        len1 = len(vals[0].entries)
        assert all(len(x.entries) == len1 for x in vals), {k: len(v.entries) for k, v in self.columns.items()}

        # We don't show the empty table
        if len1 <= 0:
            return []

        # Sort entries
        if sort_columns is None:
            lines_dict = {i: i for i in range(len1)}
        else:
            # Convert column names to columns
            sort_cols: list[Column] = []
            for name_or_obj in sort_columns:
                if isinstance(name_or_obj, str):
                    sort_cols.append(self.columns[name_or_obj])
                else:
                    sort_cols.append(name_or_obj)

            lines_dict = {}
            for i in range(len1):
                lines_dict[tuple(c.entries[i] for c in sort_cols) + (i,)] = i

        line_sep = '+-' + '-+-'.join('-' * x.width for x in self.columns.values()) + '-+'

        ret = []
        if self.heading:
            # this is a cheap hacky solution to quickly get the width
            h_width = len(line_sep) - 2
            ret.append('+' + '-' * h_width + '+')
            ret.append(f'|{self.heading:^{h_width}s}|')

        ret.append(line_sep)

        # Heading
        l1 = '|'
        for v in self.columns.values():
            l1 += f' {v.name if v.alias is None else v.alias:^{v.width}s} |'
        ret.append(l1)
        ret.append(line_sep)

        for _, i in sorted(lines_dict.items()):
            lines = max(x.count_lines(i) for x in self.columns.values())

            grid = tuple(x.format_entry(i, lines) for x in self.columns.values())  # type: tuple[list[str], ...]
            for col_i in range(lines):
                cols = [obj[col_i] for obj in grid]
                ret.append('| ' + ' | '.join(cols) + ' |')

        ret.append(line_sep)
        return ret
