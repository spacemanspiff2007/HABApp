from collections import OrderedDict
from typing import Optional, Dict, List, Union


class Column:
    def __init__(self, align: Optional[str] = None):
        self.width: int = 0
        self.align: Optional[str] = align

        self.entries = []

    def format_entry(self, pos: int) -> str:
        val = self.entries[pos]
        f = f'{{:{""if self.align is None else self.align}{self.width:d}}}'
        return f.format(val)

    def add(self, val):
        self.width = max(self.width, len(str(val)))
        self.entries.append(val)


class Table:
    def __init__(self):
        self.columns: Dict[str, Column] = OrderedDict()

    def add_column(self, name: str, align: Optional[str] = None) -> Column:
        self.columns[name] = c = Column(align)
        c.width = len(name)
        return c

    def get_lines(self, sort_columns: List[Union[str, Column]] = None):
        # check if all tables have the same length
        vals = list(self.columns.values())
        len1 = len(vals[0].entries)
        assert all(map(lambda x: len(x.entries) == len1, vals)), {k: len(v.entries) for k, v in self.columns.items()}

        # We don't show the empty
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
        ret = [line_sep]

        # Heading
        l1 = '|'
        for k, v in self.columns.items():
            l1 += f' {k:^{v.width}s} |'
        ret.append(l1)
        ret.append(line_sep)

        for t, i in sorted(lines_dict.items()):
            ret.append('| ' + ' | '.join(map(lambda x: x.format_entry(i), self.columns.values())) + ' |')

        ret.append(line_sep)
        return ret
