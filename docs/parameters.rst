
Parameters
==================================

Parameters
------------------------------
Parameters are values which can easily be changed without having to reload the rules.
Values will be picked up during runtime as soon as they get edited in the corresponding file.
If the file doesn't exist yet it will automatically be generated in the configured ``param`` folder.
Parameters are perfect for boundaries (e.g. if value is below param switch something on).
Currently there are is :class:`~HABApp.parameters.Parameter` and :class:`~HABApp.parameters.DictParameter` available.

.. exec_code::
    :hide_output:

    # ------------ hide: start ------------
    async def run():
        import HABApp
        from HABApp.parameters.parameters import _PARAMETERS
        _PARAMETERS['param_file_testrule'] = {'min_value': 10, 'Rule A': {'subkey1': {'subkey2': ['a', 'b', 'c']}}}

    # ------------ hide: stop -------------

        from HABApp import Rule, Parameter
        from HABApp.core.events import ValueChangeEventFilter

        class MyRuleWithParameters(Rule):
            def __init__(self):
                super().__init__()

                # construct parameter once, default_value can be anything
                self.min_value = Parameter( 'param_file_testrule', 'min_value', default_value=10)

                # deeper structuring is possible through specifying multiple keys
                self.min_value_nested = Parameter(
                    'param_file_testrule',
                    'Rule A', 'subkey1', 'subkey2',
                    default_value=['a', 'b', 'c'] # defaults can also be dicts or lists
                )

                self.listen_event('test_item', self.on_change_event, ValueChangeEventFilter())

            def on_change_event(self, event):

                # the parameter can be used like a normal variable, comparison works as expected
                if self.min_value < event.value:
                    pass

                # The current value can be accessed through the value-property, but don't cache it!
                current_value = self.min_value.value


        MyRuleWithParameters()

    # ------------ hide: start ------------
        HABApp.core.EventBus.post_event('test_watch', HABApp.core.events.ValueChangeEvent('test_item', 5, 6))

    from rule_runner import SimpleRuleRunner
    SimpleRuleRunner().run(run())


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

.. exec_code::
    :caption: rule

    # ------------ hide: start ------------
    async def run():
        from HABApp.parameters.parameters import _PARAMETERS
        _PARAMETERS['my_param'] = {'key1': {'v': 10}, 'key2': {'v': 12}}

    # ------------ hide: stop -------------
        import HABApp

        class MyRule(HABApp.Rule):
            def __init__(self, k, v):
                super().__init__()

                print(f'{k}: {v}')


        cfg = HABApp.DictParameter('my_param')    # this will get the file content
        for k, v in cfg.items():
            MyRule(k, v)

    # ------------ hide: start ------------
    from rule_runner import SimpleRuleRunner
    SimpleRuleRunner().run(run())


Parameter classes
------------------------------

.. autoclass:: HABApp.parameters.Parameter
   :members:


.. autoclass:: HABApp.parameters.DictParameter
   :members:
