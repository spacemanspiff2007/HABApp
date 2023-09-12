import typing
from typing import List, Optional, ClassVar

from pydantic import BaseModel

from HABApp.openhab.definitions.rest import ItemResp


class HABAppThingPluginData(BaseModel):
    obj_name: ClassVar[str] = 'ThingPlugin'

    created_link: Optional[str] = None
    created_ns: List[str] = []


# keep this up to date
cls_names = {k.obj_name: k for k in (HABAppThingPluginData, )}


def load_habapp_meta(data: ItemResp) -> ItemResp:
    meta = data.metadata
    if meta.setdefault('HABApp', None) is None:
        return data

    cls = cls_names.get(meta['HABApp']['value'])    # type: typing.Union[HABAppThingPluginData]
    meta['HABApp'] = cls.model_validate(meta['HABApp'].get('config', {}))
    return data


def get_api_vals(obj: typing.Union[HABAppThingPluginData]) -> typing.Tuple[str, dict]:
    return obj.obj_name, obj.model_dump(exclude_defaults=True)
