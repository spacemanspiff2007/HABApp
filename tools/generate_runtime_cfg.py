"""Generates a config file compatible format of configuration options"""

from pprint import pprint
from typing import TypeVar, Type, Optional

import requests
from pydantic import BaseModel, Extra, constr, StrictBool, parse_obj_as, StrictStr, validator
from requests.auth import HTTPBasicAuth


class ApiModel(BaseModel):
    class Config:
        extra = Extra.forbid


class ServiceResp(ApiModel):
    id: constr(strict=True, min_length=1)
    label: constr(strict=True)
    category: constr(strict=True, min_length=1)
    configDescriptionURI: constr(strict=True, min_length=1)
    multiple: StrictBool


class ConfigDescriptionParameter(ApiModel):
    name: constr(strict=True, min_length=1)
    label: StrictStr
    description: StrictStr

    type: constr(strict=True, min_length=1)

    readOnly: StrictBool
    required: StrictBool
    verify: StrictBool
    multiple: StrictBool
    advanced: StrictBool
    limitToOptions: StrictBool

    default: Optional[constr(strict=True, min_length=1)]
    defaultValues: Optional[list[constr(strict=True, min_length=1)]]
    context: Optional[constr(strict=True, min_length=1)]

    min: Optional[int]
    max: Optional[int]
    stepsize: Optional[int]

    unit: Optional[constr(strict=True, min_length=1)]
    unitLabel: Optional[constr(strict=True, min_length=1)]

    options: dict[str, str]

    filterCriteria: list

    @validator('options', pre=True)
    def _get_options(cls, v):
        if isinstance(v, list):
            ret = {}
            for obj in v:
                val = obj['value']
                assert val not in obj
                ret[val] = obj['label']
            return ret
        return v


class ConfigDescription(ApiModel):
    uri: constr(strict=True, min_length=1)
    parameters: list[ConfigDescriptionParameter]
    parameterGroups: list


auth = HTTPBasicAuth('asdf', 'asdf')

T = TypeVar('T')


def get_json(url: str, resp_model: Type[T]) -> T:
    assert url.startswith('/')
    ret = requests.get(f'http://localhost:8080/rest/{url}', auth=auth)
    assert ret.status_code == 200
    data = ret.json()
    try:
        return parse_obj_as(resp_model, data)
    except Exception:
        pprint(data)
        raise


services = get_json('/services', list[ServiceResp])


def sort_services(s: ServiceResp):
    category_order = ('system', 'ui', 'voice', 'misc')
    try:
        index = category_order.index(s.category)
    except ValueError:
        index = 99

    return index, s.id


services = sorted(services, key=sort_services)


descriptions: list[ConfigDescription] = []
for service in services:
    descriptions.append(get_json(f'/config-descriptions/{service.configDescriptionURI}', ConfigDescription))


def get_option_str(options: dict[str, str]) -> list[str]:
    if len(options) <= 1 or len(options) > 15 or set(param.options.keys()) == {'true', 'false'}:
        return []

    lower_keys = set(map(lambda x: x.lower(), options.keys()))
    lower_vals = set(map(lambda x: x.lower(), options.values()))
    if lower_keys == lower_vals:
        return []

    ret = [f'# {len(param.options)} value{"s" if len(param.options) != 1 else ""} are accepted:']
    for option_key, option_value in param.options.items():
        ret.append(f'#    - {option_key}: {option_value}')
    return ret


for desc in descriptions:
    # if desc.uri != 'system:sitemap':
    #     continue

    print('')
    section_parts = desc.uri.split(':', maxsplit=1)
    section = section_parts[0].upper() if section_parts[0] != 'system' else section_parts[1].upper()
    print(f'{"#" * 20} {section} {"#" * 20}\n')

    for param in desc.parameters:
        for description_line in param.description.split('<br>'):
            print(f'# {description_line}')

        if param.unitLabel:
            print(f'# The value is specified in {param.unitLabel}')

        for option_line in get_option_str(param.options):
            print(option_line)

        default = ''
        if param.defaultValues:
            default = str(param.defaultValues)
        elif param.default:
            default = param.default

        print('#')
        print(f'#{desc.uri}:{param.name}={default}\n')
