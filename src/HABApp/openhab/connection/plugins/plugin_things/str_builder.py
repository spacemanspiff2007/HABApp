import re
from typing import Optional, Dict, Tuple, Pattern, Union

from .filters import THING_ALIAS, CHANNEL_ALIAS


SEPARATOR = ','
RE_PLACEHOLDERS = re.compile(r'{([^}]+)}')
RE_ACCESSOR = re.compile(f'(?P<accessor>[^{SEPARATOR}]+)(?:{SEPARATOR}(?P<operator>.+))?')


class StrBuilder:
    def __init__(self, value: str):
        self.template: str = value.strip()
        self.regex: Dict[str, Tuple[str, Optional[Pattern], Optional[str]]] = {}

        for p in RE_PLACEHOLDERS.findall(value):
            m = RE_ACCESSOR.fullmatch(p)
            accessor = m.group('accessor')
            operator = m.group('operator')

            regex, replace = None, None

            if operator is not None:
                p_comma = operator.rfind(SEPARATOR)
                if p_comma == -1:
                    search = operator
                else:
                    search = operator[:p_comma]
                    replace = operator[p_comma + 1:].strip()

                try:
                    search = search.strip()
                    regex = re.compile(search, re.IGNORECASE)
                    if replace is None and not regex.groups:
                        raise ValueError(f'Pattern {search} does not have a group!')
                except re.error as e:
                    raise ValueError(f'Could not compile regex "{search}": {e}') from None

            assert accessor in THING_ALIAS or accessor in CHANNEL_ALIAS, accessor
            self.regex[f'{{{p}}}'] = accessor.strip(), regex, replace

    def get_str(self, context: Dict[str, str]) -> str:
        out = self.template
        for search, p in self.regex.items():
            accessor, regex, replace = p

            if regex is None:
                out = out.replace(search, context[accessor])
                continue

            if replace is not None:
                val = regex.sub(replace, context[accessor])
            else:
                m = regex.search(context[accessor])
                if m is None:
                    raise ValueError(f'Regex "{regex.pattern}" did not match "{context[accessor]}"')
                val = m.group(1)
            out = out.replace(search, val.strip())

        return out

    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.template}">'


def apply_builder(_in: Union[dict, list], context: dict):
    if isinstance(_in, StrBuilder):
        return _in.get_str(context)

    if isinstance(_in, list):
        ret = []
        for k in _in:
            if isinstance(k, StrBuilder):
                k = k.get_str(context)
            elif isinstance(k, (list, dict)):
                k = apply_builder(k, context)
            ret.append(k)
    else:
        ret = {}
        for k, v in _in.items():
            if isinstance(k, StrBuilder):
                k = k.get_str(context)

            if isinstance(v, StrBuilder):
                v = v.get_str(context)
            elif isinstance(v, (list, dict)):
                v = apply_builder(v, context)
            ret[k] = v
    return ret
