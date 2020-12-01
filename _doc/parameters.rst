
Parameters
==================================

Parameters
------------------------------
Parameters are values which can easily be changed without having to reload the rules.
Values will be picked up during runtime as soon as they get edited in the corresponding file.
If the file doesn't exist yet it will automatically be generated in the configured `param` folder.
Parameters are perfect for boundaries (e.g. if value is below param switch something on).
Currently there are is :class:`~HABApp.parameters.Parameter` and :class:`~HABApp.parameters.DictParameter` available.

.. execute_code::
    :hide_output:

    # hide
    from HABApp.parameters.parameters import _PARAMETERS
    _PARAMETERS['param_file_testrule'] = {'min_value': 10, 'Rule A': {'subkey1': {'subkey2': ['a', 'b', 'c']}}}

    from tests import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    # hide

    import HABApp

    class MyRuleWithParameters(HABApp.Rule):
        def __init__(self):
            super().__init__()

            # construct parameter once, default_value can be anything
            self.min_value = HABApp.Parameter( 'param_file_testrule', 'min_value', default_value=10)

            # deeper structuring is possible through specifying multiple keys
            self.min_value_nested = HABApp.Parameter(
                'param_file_testrule',
                'Rule A', 'subkey1', 'subkey2',
                default_value=['a', 'b', 'c'] # defaults can also be dicts or lists
            )

            self.listen_event('test_item', self.on_change_event, HABApp.core.events.ValueChangeEvent)

        def on_change_event(self, event):

            # the parameter can be used like a normal variable, comparison works as expected
            if self.min_value < event.value:
                pass

            # The current value can be accessed through the value-property, but don't cache it!
            current_value = self.min_value.value


    MyRuleWithParameters()

    # hide
    HABApp.core.EventBus.post_event('test_watch', HABApp.core.events.ValueChangeEvent('test_item', 5, 6))
    runner.tear_down()
    # hide

Created file:

.. code-block:: yaml

   min_value: 10
   Rule A:
       subkey1:
           subkey2:
               - a
               - b
               - c

Changes in the file will be automatically picked up through :class:`~HABApp.parameters.Parameter`.


Validation
------------------------------
Since parameters used to provide flexible configuration for automation classes they can get quite complex and
error prone. Thus it is possible to provide a validator for a file which will check the files for constraints,
missing keys etc. when the file is loaded.

.. autofunction:: HABApp.parameters.set_file_validator

Example

.. execute_code::
    :hide_output:

    # hide
    from pathlib import Path

    import HABApp
    from HABApp.parameters.parameters import _PARAMETERS
    _PARAMETERS['param_file_testrule'] = {'min_value': 10, 'Rule A': {'subkey1': {'subkey2': ['a', 'b', 'c']}}}

    # Patch values so we don't get errors
    HABApp.config.CONFIG.directories.rules = Path('/my_rules/')
    HABApp.config.CONFIG.directories.config = Path('/my_config/')
    HABApp.config.CONFIG.directories.param = Path('/my_param/')
    # hide

    import HABApp
    import voluptuous

    # Validator can even and should be specified before loading rules

    # allows a dict e.g. { 'key1': {'key2': '5}}
    HABApp.parameters.set_file_validator('file1', {str: {str: int}})

    # More complex example with an optional key:
    validator = {
        'Test': int,
        'Key': {
            'mandatory_key': str,
            voluptuous.Optional('optional'): int
        }
    }
    HABApp.parameters.set_file_validator('file1', validator)


Create rules from Parameters
------------------------------
Parameteres are not bound to rule instance and thus work everywhere in the rule file.
It is possible to dynamically create rules from the contents of the parameter file.

It's even possible to automatically reload rules if the parameter file has changed:
Just add the "reloads on" entry to the file.


.. code-block:: yaml
   :caption: my_param.yml

    key1:
      v: 10
    key2:
      v: 12

.. execute_code::
    :header_code: rule

    # hide
    from HABApp.parameters.parameters import _PARAMETERS
    _PARAMETERS['my_param'] = {'key1': {'v': 10}, 'key2': {'v': 12}}

    from tests import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    # hide



    import HABApp

    class MyRule(HABApp.Rule):
        def __init__(self, k, v):
            super().__init__()

            print(f'{k}: {v}')


    cfg = HABApp.DictParameter('my_param')    # this will get the file content
    for k, v in cfg.items():
        MyRule(k, v)

    # hide
    runner.tear_down()
    # hide



Parameter classes
------------------------------

.. autoclass:: HABApp.parameters.Parameter
   :members:


.. autoclass:: HABApp.parameters.DictParameter
   :members:

