import dataclasses
import typing


@dataclasses.dataclass
class OpenhabItemDefinition:
    """
    :ivar str type: item type
    :ivar str name: item name
    :ivar typing.Any state: item state
    :ivar str state: item label
    :ivar str category: item category
    :ivar bool editable: item can changed through Rest API
    :ivar typing.List[str] tags: item tags
    :ivar typing.List[str] groups: groups the item is in
    :ivar typing.List[OpenhabItemDefinition] members: If the item is a group this contains the members
    """
    type: str
    name: str
    state: typing.Any
    label: str = ''
    category: str = ''
    editable: bool = True
    tags: typing.List[str] = dataclasses.field(default_factory=list)
    groups: typing.List[str] = dataclasses.field(default_factory=list)
    members: 'typing.List[OpenhabItemDefinition]' = dataclasses.field(default_factory=list)

    @classmethod
    def from_dict(cls, data) -> 'OpenhabItemDefinition':
        assert isinstance(data, dict), type(dict)
        data['groups'] = data.pop('groupNames', [])

        # remove link
        data.pop('link', None)

        # map states, quick n dirty
        state = data['state']
        if state == 'NULL':
            state = None
        else:
            try:
                state = int(state)
            except ValueError:
                try:
                    state = float(state)
                except ValueError:
                    pass
        data['state'] = state

        for i, item in enumerate(data.get('members', [])):
            data['members'][i] = cls.from_dict(item)

        # Important, sometimes OpenHAB returns more than in the schema spec, so we remove those items otherwise we
        # get e.g.: TypeError: __init__() got an unexpected keyword argument 'stateDescription'
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclasses.dataclass
class OpenhabThingChannelDefinition:
    uid: typing.Optional[str] = None
    id: typing.Optional[str] = None
    channelTypeUID: typing.Optional[str] = None
    itemType: typing.Optional[str] = None
    kind: typing.Optional[str] = None
    label: typing.Optional[str] = None
    description: typing.Optional[str] = None
    defaultTags: typing.Optional[typing.List[str]] = None
    properties: typing.Optional[typing.Dict[str, typing.Any]] = None
    configuration: typing.Optional[typing.Dict[str, typing.Any]] = None



@dataclasses.dataclass
class OpenhabThingDefinition:
    label: typing.Optional[str] = None
    bridgeUID: typing.Optional[str] = None
    configuration: typing.Dict[str, typing.Any] = None
    properties: typing.Dict[str, typing.Any] = None
    UID: typing.Optional[str] = None
    thingTypeUID: typing.Optional[str] = None
    channels: typing.Optional[typing.List[OpenhabThingChannelDefinition]] = None
    location: typing.Optional[str] = None
    statusInfo: typing.Optional[typing.Dict[str, str]] = None
    firmwareStatus: typing.Optional[typing.Dict[str, str]] = None
    editable: typing.Optional[bool] = None

    @classmethod
    def from_dict(cls, data) -> 'OpenhabThingDefinition':
        assert isinstance(data, dict), type(dict)

        # convert channel objs to dataclasses
        channels = data.get('channels')
        if channels is not None:
            data['channels'] = [OpenhabThingChannelDefinition(**kw) for kw in channels]

        return cls(**data)


class ThingNotFoundError(Exception):
    pass


class ThingNotEditableError(Exception):
    pass
