import time

from HABApp.openhab.connection.plugins.plugin_things.plugin_things import TextualThingConfigPlugin
from tests.helpers import LogCollector, MockFile, TestEventBus


async def test_errors(test_logs: LogCollector, eb: TestEventBus):
    eb.allow_errors = True

    cfg = TextualThingConfigPlugin()

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

    cfg.cache_cfg = data
    cfg.cache_ts = time.time()
    await cfg.file_load('/thing_test.yml', file)

    test_logs.add_expected(None, 'ERROR', 'Duplicate item: Name1')

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

    cfg.cache_cfg = data
    cfg.cache_ts = time.time()
    await cfg.file_load('/thing_test.yml', file)

    test_logs.add_expected(None, 'ERROR', '"â_ß_{_)" is not a valid name for an item!')
    test_logs.add_expected(None, 'ERROR', "   (created for {'channel_uid': 'astro:sun:1d5f16df:rise#start', "
                                          "'channel_type': 'astro:start', 'channel_label': 'Startzeit', "
                                          "'channel_kind': 'STATE', 'thing_uid': 'astro:sun:1d5f16df', "
                                          "'thing_type': 'astro:sun', 'thing_location': '', "
                                          "'thing_label': 'Astronomische Sonnendaten', "
                                          "'bridge_uid': '', 'editable': True})")

    cfg.do_cleanup.cancel()
