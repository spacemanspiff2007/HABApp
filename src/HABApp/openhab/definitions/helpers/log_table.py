from collections import OrderedDict
from typing import Optional, Dict, List, Union, Tuple, Any


class Column:
    wrap: int = 80

    def __init__(self, name: str, align: Optional[str] = None, alias: Optional[str] = None, wrap: Optional[int] = None):
        self.name: str = name
        self.alias: Optional[str] = alias

        self.align: Optional[str] = align
        if wrap is not None:
            self.wrap = wrap

        self.width: int = len(name) if alias is None else len(alias)
        self.entries: List[Tuple[Any, ...]] = []

    def get_lines(self, pos: int) -> int:
        return len(self.entries[pos])

    def format_entry(self, pos: int, lines: int) -> List[str]:
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

    def add(self, val):
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

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}'


class Table:
    def __init__(self, heading: str = ''):
        self.columns: Dict[str, Column] = OrderedDict()
        self.heading: str = heading

    def add_column(self, name: str, align: Optional[str] = None, alias: Optional[str] = None,
                   wrap: Optional[int] = None) -> Column:
        self.columns[name] = c = Column(name, align, alias, wrap)
        return c

    def add_dict(self, _in: dict):
        for k, col in self.columns.items():
            col.add(_in[k])

    def get_lines(self, sort_columns: List[Union[str, Column]] = None) -> List[str]:
        # check if all tables have the same length
        vals = list(self.columns.values())
        len1 = len(vals[0].entries)
        assert all(map(lambda x: len(x.entries) == len1, vals)), {k: len(v.entries) for k, v in self.columns.items()}

        # We don't show the empty table
        if len1 <= 0:
            return []

        # Sort entries
        if sort_columns is None:
            lines_dict = {i: i for i in range(len1)}
        else:
            # Convert column names to columns
            for i, e in enumerate(sort_columns):
                if isinstance(e, str):
                    sort_columns[i] = self.columns[e]

            lines_dict = {}
            for i in range(len1):
                lines_dict[tuple(c.entries[i] for c in sort_columns) + (i,)] = i

        line_sep = '+-' + '-+-'.join(map(lambda x: '-' * x.width, self.columns.values())) + '-+'

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

        for t, i in sorted(lines_dict.items()):
            lines = max(map(lambda x: x.get_lines(i), self.columns.values()))

            grid = tuple(map(lambda x: x.format_entry(i, lines), self.columns.values()))  # type: Tuple[List[str], ...]
            for col_i in range(lines):
                cols = [obj[col_i] for obj in grid]
                ret.append('| ' + ' | '.join(cols) + ' |')

        ret.append(line_sep)
        return ret
