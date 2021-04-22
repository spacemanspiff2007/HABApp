import typing
from typing import List, Optional

from pydantic import BaseModel


class HABAppThingPluginData(BaseModel):
    _val_name = 'ThingPlugin'

    created_link: Optional[str]
    created_ns: List[str] = []


# keep this up to date
cls_names = {k._val_name: k for k in (HABAppThingPluginData, )}


def load_habapp_meta(data: dict) -> dict:
    meta = data.setdefault('metadata', {})
    if meta.setdefault('HABApp', None) is None:
        return data

    cls = cls_names.get(meta['HABApp']['value'])    # type: typing.Union[HABAppThingPluginData]
    meta['HABApp'] = cls.parse_obj(meta['HABApp'].get('config', {}))
    return data


def get_api_vals(obj: typing.Union[HABAppThingPluginData]) -> typing.Tuple[str, dict]:
    return obj._val_name, obj.dict(exclude_defaults=True)
