**************************************
Class reference
**************************************

Reference for returned classes from some functions.
These are not intended to be created by the user.

Watches
======================================


ItemNoUpdateWatch
""""""""""""""""""""""""""""""""""""""

.. autoclass:: HABApp.core.items.base_item_watch.ItemNoUpdateWatch
   :members:
   :inherited-members:
   :member-order: groupwise

ItemNoChangeWatch
""""""""""""""""""""""""""""""""""""""

.. autoclass:: HABApp.core.items.base_item_watch.ItemNoChangeWatch
   :members:
   :inherited-members:
   :member-order: groupwise


Scheduler
======================================


OneTimeJob
""""""""""""""""""""""""""""""""""""""

.. autoclass:: eascheduler.jobs.OneTimeJob
   :members:
   :inherited-members:
   :member-order: groupwise

CountdownJob
""""""""""""""""""""""""""""""""""""""

.. autoclass:: eascheduler.jobs.CountdownJob
   :members:
   :inherited-members:
   :member-order: groupwise

ReoccurringJob
""""""""""""""""""""""""""""""""""""""

.. autoclass:: eascheduler.jobs.ReoccurringJob
   :members:
   :inherited-members:
   :member-order: groupwise

DayOfWeekJob
""""""""""""""""""""""""""""""""""""""

.. autoclass:: eascheduler.jobs.DayOfWeekJob
   :members:
   :inherited-members:
   :member-order: groupwise

DawnJob
""""""""""""""""""""""""""""""""""""""

.. autoclass:: eascheduler.jobs.DawnJob
   :members:
   :inherited-members:
   :member-order: groupwise

SunriseJob
""""""""""""""""""""""""""""""""""""""

.. autoclass:: eascheduler.jobs.SunriseJob
   :members:
   :inherited-members:
   :member-order: groupwise

SunsetJob
""""""""""""""""""""""""""""""""""""""

.. autoclass:: eascheduler.jobs.SunsetJob
   :members:
   :inherited-members:
   :member-order: groupwise

DuskJob
""""""""""""""""""""""""""""""""""""""

.. autoclass:: eascheduler.jobs.DuskJob
   :members:
   :inherited-members:
   :member-order: groupwise



.. _ref_configuration_reference:

Configuration
======================================

.. autopydantic_model:: HABApp.config.models.ApplicationConfig

Directories
""""""""""""""""""""""""""""""""""""""

.. autopydantic_model:: HABApp.config.models.directories.DirectoriesConfig
   :exclude-members: create_folders

Location
""""""""""""""""""""""""""""""""""""""

.. autopydantic_model:: HABApp.config.models.location.LocationConfig

MQTT
""""""""""""""""""""""""""""""""""""""

.. py:currentmodule:: HABApp.config.models.mqtt

.. autopydantic_model:: MqttConfig

.. autopydantic_model:: Connection
.. autopydantic_model:: TLSSettings
.. autopydantic_model:: Subscribe
.. autopydantic_model:: Publish
.. autopydantic_model:: General

Openhab
""""""""""""""""""""""""""""""""""""""

.. py:currentmodule:: HABApp.config.models.openhab

.. autopydantic_model:: OpenhabConfig

.. autopydantic_model:: Connection
.. autopydantic_model:: Ping
.. autopydantic_model:: General

HABApp
""""""""""""""""""""""""""""""""""""""

.. py:currentmodule:: HABApp.config.models.habapp

.. autopydantic_model:: HABAppConfig

.. autopydantic_model:: ThreadPoolConfig
