
Parameters
==================================

Parameters
------------------------------
Parameters are values which can easily be changed without having to reload the rules.
Values will be picked up during runtime as soon as they get edited in the corresponding file.
If the file doesn't exist yet it will automatically be generated in the configured ``param`` folder.
Parameters are perfect for boundaries (e.g. if value is below param switch something on).

Available parameter classes:
 - :class:`~HABApp.parameters.Parameter` - untyped, accepts any value
 - :class:`~HABApp.parameters.StrParameter`, :class:`~HABApp.parameters.IntParameter`,
   :class:`~HABApp.parameters.FloatParameter`, :class:`~HABApp.parameters.NumberParameter` - typed
   :class:`~HABApp.parameters.Parameter` variants that raise a ``TypeError`` if the value in the
   file does not match the expected type
 - :class:`~HABApp.parameters.DictParameter` - returns the complete (nested) file content
 - :class:`~HABApp.parameters.BaseModelParameter` - validates the value against a pydantic model on every access

.. exec_code::
    :hide_output:

    # ------------ hide: start ------------
    async def run(provider):
        import HABApp
        from HABApp.parameters.registry import ParameterRegistry
        registry = provider.get_existing(ParameterRegistry)
        registry._get_or_create_file('param_file_testrule').data = \
            {'min_value': 10, 'Rule A': {'subkey1': {'subkey2': ['a', 'b', 'c']}}}

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
        from HABApp.core.internals import EventBus
        eb = provider.get_existing(EventBus)
        eb.post_event('test_watch', HABApp.core.events.ValueChangeEvent('test_item', 5, 6))

    import doc_runner
    doc_runner.run(run)


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
    async def run(provider):
        from HABApp.parameters.registry import ParameterRegistry
        provider.get_existing(ParameterRegistry)._get_or_create_file('my_param').data = \
            {'key1': {'v': 10}, 'key2': {'v': 12}}

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
    import doc_runner
    doc_runner.run(run)


Typed parameters
------------------------------
:class:`~HABApp.parameters.Parameter` accepts any value type. If the value in the file has to be of a
specific type use one of the typed subclasses instead - they raise a ``TypeError`` on access if the
value in the file does not match:

.. code-block:: python

    from HABApp.parameters import StrParameter, IntParameter, FloatParameter, NumberParameter

    name = StrParameter('my_param', 'name', default_value='Bob')      # only accepts str
    count = IntParameter('my_param', 'count', default_value=1)        # only accepts int
    ratio = FloatParameter('my_param', 'ratio', default_value=0.5)    # only accepts float
    limit = NumberParameter('my_param', 'limit', default_value=10)    # accepts int or float


Validating parameter files
------------------------------
The complete content of a parameter file can be validated against a
`pydantic <https://docs.pydantic.dev/>`_ model with :func:`~HABApp.parameters.set_file_validator`.
The file is (re-)validated every time it is loaded - if the validation fails the file will not be
loaded and the error is logged.

.. code-block:: python

    from pydantic import BaseModel
    from HABApp.parameters import set_file_validator

    class MyParamModel(BaseModel):
        min_value: int = 10

    # set the file validator
    set_file_validator('param_file_testrule', MyParamModel)

    # remove the validator again
    set_file_validator('param_file_testrule', None)


Validating individual parameters
------------------------------------
If only a part of a file should be validated use :class:`~HABApp.parameters.BaseModelParameter`
instead. The value is validated against the model on every access, so it also works if the value
of a single key changes independently of the rest of the file.

.. code-block:: python

    from pydantic import BaseModel
    from HABApp import BaseModelParameter

    class SubModel(BaseModel):
        subkey2: list[str]

    param = BaseModelParameter('param_file_testrule', 'Rule A', 'subkey1', model=SubModel)
    param.value.subkey2  # -> ['a', 'b', 'c'], validated & parsed as SubModel


Parameter classes
------------------------------

.. autoclass:: HABApp.parameters.Parameter
   :members:

.. autoclass:: HABApp.parameters.StrParameter
   :members:

.. autoclass:: HABApp.parameters.IntParameter
   :members:

.. autoclass:: HABApp.parameters.FloatParameter
   :members:

.. autoclass:: HABApp.parameters.NumberParameter
   :members:

.. autoclass:: HABApp.parameters.DictParameter
   :members:

.. autoclass:: HABApp.parameters.BaseModelParameter
   :members:

.. autofunction:: HABApp.parameters.set_file_validator
