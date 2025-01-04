
Advanced Usage
==================================

HABApp Topics
------------------------------
There are several internal topics which can be used to react to HABApp changes from within rules.
An example would be dynamically reloading files or an own notifier in case there are errors (e.g. Pushover).

.. list-table::
   :widths: auto
   :header-rows: 1

   * - Topic
     - Description
     - Events

   * - HABApp.Files
     - The corresponding events trigger a load/unload of the file specified in the event
     - :class:`~HABApp.core.events.habapp_events.RequestFileLoadEvent` and :class:`~HABApp.core.events.habapp_events.RequestFileUnloadEvent`

   * - HABApp.Infos
     - All infos in functions and rules of HABApp create an according event
     - ``str``

   * - HABApp.Warnings
     - All warnings in functions (e.g. caught exceptions) and rules of HABApp create an according event
     - :class:`~HABApp.core.events.habapp_events.HABAppException` or ``str``

   * - HABApp.Errors
     - All errors in functions and rules of HABApp create an according event. Use this topic to create an own notifier
       in case of errors (e.g. Pushover).
     - :class:`~HABApp.core.events.habapp_events.HABAppException` or ``str``



.. autoclass:: HABApp.core.events.habapp_events.RequestFileLoadEvent
   :members:

.. autoclass:: HABApp.core.events.habapp_events.RequestFileUnloadEvent
   :members:

.. autoclass:: HABApp.core.events.habapp_events.HABAppException
   :members:

File properties
------------------------------
For every HABApp file it is possible to specify some properties.
The properties are specified as a comment (prefixed with ``#``) somewhere at the beginning of the file
and are in the yml format.
Make sure **no empty line** is before the property definition in the file.
They keyword ``HABApp`` can be arbitrarily intended.

.. hint::
  File names are not absolute but relative with a folder specific prefix.
  It's best to use the file name from the :class:`~HABApp.core.events.habapp_events.RequestFileLoadEvent`
  from the HABApp event bus.

Configuration format

.. code-block:: yaml

    HABApp:
      depends on:
       - filename
      reloads on:
       - filename

.. list-table::
   :widths: auto
   :header-rows: 1

   * - Property
     - Description

   * - ``depends on``
     - The file will only get loaded when **all** of the files specified as dependencies have been successfully loaded

   * - ``reloads on``
     - The file will get automatically reloaded when **one of** the files specified will be reloaded


Example

.. code-block:: python

   # Some other stuff
   #
   # HABApp:
   #   depends on:
   #    - rules/rule_file.py
   #   reloads on:
   #    - param/param_file.yml

   import HABApp
   ...


.. _ref_run_code_on_startup:

Running Python code on startup
------------------------------

It's possible to run arbitrary code during the startup of HABApp. This can be achieved by creating a module/package
called ``HABAppUser``. HABApp will try to import it before loading the configuration and thus execute the code.
The module/package must be importable so it has to be in one of the ``PATH``/``PYTHONPATH`` folders or in the current
working directory.


Invoking openHAB actions
------------------------
The openHAB REST interface does not expose `actions <https://www.openhab.org/docs/configuration/actions.html>`_,
and thus there is no way to trigger them from HABApp. Even if it is not possible to create an openHAB item that
directly triggers the action, there is a way to work around it with additional items within openHAB.
An additional openHAB (note not HABapp) rule listens to changes on those items and invokes the appropriate
openHAB actions.
On the HABApp side these actions are indirectly executed by setting the values for those items.

Below is an example how to invoke the openHAB Audio and Voice actions.

First, define a couple of items to accept values from HABApp, and place them in /etc/openhab2/items/habapp-bridge.items:

.. code-block:: text

   String AudioVoiceSinkName

   String TextToSpeechMessage
   String AudioFileLocation
   String AudioStreamUrl

Second, create the JSR223 script to invoke the actions upon changes in the values of the items above.

.. code-block:: python

   from core import osgi
   from core.jsr223 import scope
   from core.rules import rule
   from core.triggers import when
   from org.eclipse.smarthome.model.script.actions import Audio
   from org.eclipse.smarthome.model.script.actions import Voice

   SINK_ITEM_NAME = 'AudioVoiceSinkName'

   @rule("Play voice TTS message")
   @when("Item TextToSpeechMessage changed")
   def onTextToSpeechMessageChanged(event):
       ttl = scope.items[event.itemName].toString()
       if ttl is not None and ttl != '':
           Voice.say(ttl, None, scope.items[SINK_ITEM_NAME].toString())

           # reset the item to wait for the next message.
           scope.events.sendCommand(event.itemName, '')

   @rule("Play audio stream URL")
   @when("Item AudioStreamUrl changed")
   def onAudioStreamURLChanged(event):
       stream_url = scope.items[event.itemName].toString()
       if stream_url is not None and stream_url != '':
           Audio.playStream(scope.items[SINK_ITEM_NAME].toString(), stream_url)

           # reset the item to wait for the next message.
           scope.events.sendCommand(event.itemName, '')

   @rule("Play local audio file")
   @when("Item AudioFileLocation changed")
   def onAudioFileLocationChanged(event):
       file_location = scope.items[event.itemName].toString()
       if file_location is not None and file_location != '':
           Audio.playSound(scope.items[SINK_ITEM_NAME].toString(), file_location)

           # reset the item to wait for the next message.
           scope.events.sendCommand(event.itemName, '')

Finally, define the HABApp functions to indirectly invoke the actions:

.. code-block:: python

   def play_local_audio_file(sink_name: str, file_location: str):
       """ Plays a local audio file on the given audio sink. """
       HABApp.openhab.interface_sync.send_command(ACTION_AUDIO_SINK_ITEM_NAME, sink_name)
       HABApp.openhab.interface_sync.send_command(ACTION_AUDIO_LOCAL_FILE_LOCATION_ITEM_NAME, file_location)


   def play_stream_url(sink_name: str, url: str):
       """ Plays a stream URL on the given audio sink. """
       HABApp.openhab.interface_sync.send_command(ACTION_AUDIO_SINK_ITEM_NAME, sink_name)
       HABApp.openhab.interface_sync.send_command(ACTION_AUDIO_STREAM_URL_ITEM_NAME, url)


   def play_text_to_speech_message(sink_name: str, tts: str):
       """ Plays a text to speech message on the given audio sink. """
       HABApp.openhab.interface_sync.send_command(ACTION_AUDIO_SINK_ITEM_NAME, sink_name)
       HABApp.openhab.interface_sync.send_command(ACTION_TEXT_TO_SPEECH_MESSAGE_ITEM_NAME, tts)


Mocking openHAB items and events for tests
--------------------------------------------
It is possible to create mock items in HABApp which do not exist in openHAB to create unit tests for rules and libraries.
Ensure that this mechanism is only used for testing because since the items will not exist in openHAB they will not get
updated which can lead to hard to track down errors.

Examples:

Add an openHAB mock item to the item registry

.. exec_code::
   :hide_output:

   # ------------ hide: start ------------
   from rule_runner import SimpleRuleRunner
   SimpleRuleRunner().set_up()
   # ------------ hide: stop -------------

   import HABApp
   from HABApp.openhab.items import SwitchItem

   item = SwitchItem('my_switch', 'ON')
   HABApp.core.Items.add_item(item)

Remove the mock item from the registry:

.. exec_code::
   :hide_output:

   # ------------ hide: start ------------
   from rule_runner import SimpleRuleRunner
   SimpleRuleRunner().set_up()

   import HABApp
   from HABApp.openhab.items import SwitchItem
   HABApp.core.Items.add_item(SwitchItem('my_switch', 'ON'))
    # ------------ hide: stop -------------

   HABApp.core.Items.pop_item('my_switch')

Note that there are some item methods that encapsulate communication with openhab
(e.g.: ``SwitchItem.on(), SwitchItem.off(), and DimmerItem.percentage()``)
These currently do not work with the mock items. The state has to be changed like
any internal item.

.. exec_code::
   :hide_output:

   # ------------ hide: start ------------
   from rule_runner import SimpleRuleRunner
   SimpleRuleRunner().set_up()
   # ------------ hide: stop -------------

   import HABApp
   from HABApp.openhab.items import SwitchItem
   from HABApp.openhab.definitions import OnOffValue

   item = SwitchItem('my_switch', 'ON')
   HABApp.core.Items.add_item(item)

   item.set_value(OnOffValue.ON)    # without bus event
   item.post_value(OnOffValue.OFF)  # with bus event
