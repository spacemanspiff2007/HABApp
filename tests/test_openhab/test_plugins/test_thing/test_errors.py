import pytest

from HABApp.openhab.connection_logic.plugin_things.plugin_things import ManualThingConfig
from tests.helpers import MockFile


@pytest.mark.asyncio
async def test_errors(caplog):

    cfg = ManualThingConfig()

    data = [{"statusInfo": {"status": "ONLINE", "statusDetail": "NONE"}, "editable": True,
             "label": "Astronomische Sonnendaten",
             "configuration": {"interval": 120, "geolocation": "26.399750112407446,34.980468750000014"},
             "properties": {}, "UID": "astro:sun:1d5f16df", "thingTypeUID": "astro:sun", "channels": [
            {"linkedItems": [], "uid": "astro:sun:1d5f16df:rise#start", "id": "rise#start",
             "channelTypeUID": "astro:start", "itemType": "DateTime", "kind": "STATE", "label": "Startzeit",
             "description": "Die Startzeit des Ereignisses", "defaultTags": [], "properties": {},
             "configuration": {"offset": 0}}, ]}]

    text = """
    test: False

    filter:
      thing_type: astro:sun

    channels:
      - filter:
          channel_type: astro:start
        link items:
          - type: Number
            name: Name1
          - type: Number
            name: Name1
        """
    file = MockFile('/thing_test.yml', data=text)
    file.warn_on_delete = False

    await cfg.update_thing_config(file, data)

    assert caplog.records[0].message == 'Duplicate item: Name1'

    text = """
test: False

filter:
  thing_type: astro:sun

channels:
  - filter:
      channel_type: astro:start
    link items:
      - type: Number
        name: â ß { )
    """
    file = MockFile('/thing_test.yml', data=text)
    file.warn_on_delete = False

    await cfg.update_thing_config(file, data)

    assert caplog.records[1].message == '"â_ß_{_)" is not a valid name for an item!'
