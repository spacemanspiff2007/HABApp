.. module:: HABApp

Parameters
==================================

Parameters
------------------------------
Parameters are values which can easily be changed without having to reload the rules.
Values will be picked up during runtime as soon as they get edited in the corresponding file.
If the file doesn't exist yet it will automatically be generated in the configured `param` folder.
Parameters are perfect for boundaries (e.g. if value is below param switch something on).


Example::

    import HABApp

    def __init__(self):
        super().__init__()

        # construct parameter once, default_value can be anything
        self.min_value = HABApp.Parameters.get_parameter( 'param_file_testrule', 'min_value', default_value=10)

        # deeper structuring is possible through specifying multiple keys
        self.min_value_nested = HABApp.Parameters.get_parameter(
            'param_file_testrule',
            'Rule A', 'subkey1', 'subkey2',
            default_value=['a', 'b', 'c'] # defaults can also be dicts or lists
        )

    def on_change_event( event):
        # the parameter can be used like a normal variable, comparison works as expected
        if self.min_value < event.value:
            pass


Created file:

.. code-block:: yaml

   min_value: 10
   Rule A:
       subkey1:
           subkey2:
               - a
               - b
               - c


.. automodule:: HABApp.Parameters
   :members: get_parameter, get_parameter_value

.. autoclass:: HABApp.Parameters.rule_parameter.RuleParameter
   :members:
