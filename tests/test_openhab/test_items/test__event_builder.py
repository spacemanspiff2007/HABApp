import pytest

from HABApp.openhab.definitions.websockets.item_value_types import DecimalTypeModel, UnDefTypeModel
from HABApp.openhab.items._event_builder import OutgoingStateEvent


def test_converter() -> None:
    a = OutgoingStateEvent('Asdf', UnDefTypeModel)
    b = a | DecimalTypeModel

    assert a.create_event('name', None).payload == UnDefTypeModel(type='UnDef', value='NULL')
    assert b.create_event('name', None).payload == UnDefTypeModel(type='UnDef', value='NULL')

    with pytest.raises(ValueError):
        a.create_event('name', 1)
    assert b.create_event('name', 1).payload == DecimalTypeModel(type='Decimal', value='1')

    assert str(b) == 'OutgoingStateEventAsdf(UnDefTypeModel, DecimalTypeModel)'
