**************************************
Configuration
**************************************

Description
======================================

Configuration is done through ``config.yml`` The parent folder of the file can be specified with ``-c PATH`` or ``--config PATH``.
If nothing is specified the file ``config.yml`` is searched in the subdirectory ``HABApp`` in

* the current working directory
* the venv directory
* the user home

If the config does not yet exist in the folder a blank configuration will be created


Example
======================================
.. code-block:: yaml

    directories:
        logging: log    # If the filename for the logfile in logging.yml is not absolute it will be placed in this directory
        rules: rules    # All *.py files in this folder (and subfolders) will be loaded. Load order will be alphabetical by path.
        param: param    # Optional, this is the folder where the parameter files will be created and loaded from
        config: config  # Folder from which configuration files for openHAB will be loaded
        lib: lib        # Custom modules, libraries and files can be placed there.
                        # (!) Attention (!):
                        # Don't create rule instances in files inside the lib folder! It will lead to strange behaviour.


    # Specify the location where your HABApp instance is running
    location:
        # The coordinates are used to calculate the Sunrise/Sunset etc
        latitude: 0.0
        longitude: 0.0
        elevation: 0.0
        # The country and optional subdivision is used to calculate the holidays
        country: DE       # ISO 3166-1 Alpha-2 country code - here Germany
        subdivision: BE   # ISO 3166-2 Subdivision code or alias - here Berlin


    openhab:
        ping:
            enabled: true        # If enabled the configured item will show how long it takes to send an update from HABApp
                                 # and get the updated value back in milliseconds
            item: 'HABApp_Ping'  # Name of the NumberItem that will show the ping
            interval: 10         # Seconds between two pings

        connection:
            url: http://localhost:8080
            user: ''
            password: ''

        general:
            listen_only: False  # If True  HABApp will not change any value on the openHAB instance.
                                # Useful for testing rules from another machine.
            wait_for_openhab: True   # If True HABApp will wait for items from the openHAB instance
                                     # before loading any rules on startup


    mqtt:
        connection:
            identifier: HABApp
            host: ''
            port: 8883
            user: ''
            password: ''
            tls:
              enabled: false   # Enable TLS for the connection
              insecure: false  # Validate server hostname in server certificate
              ca cert: ''      # Path to a CA certificate that will be treated as trusted
                               # (e.g. when using a self signed certificate)

        subscribe:         # Changes to Subscribe get picked up without restarting HABApp
            qos: 0         # Default QoS for subscribing
            topics:
            - '#'               # Subscribe to this topic, qos is default QoS
            - ['my/topic', 1]   # Subscribe to this topic with explicit QoS

        publish:
            qos: 0          # Default QoS when publishing values
            retain: false   # Default retain flag when publishing values

        general:
            listen_only: False # If True  HABApp will not publish any value to the broker.
                               # Useful for testing rules from another machine.


It's possible to use environment variables and files (e.g. docker secrets) in the configuration.
See `the easyconfig documentation <https://easyconfig.readthedocs.io>`_ for the exact syntax and examples.


Configuration Reference
======================================

All possible configuration options are described here. Not all entries are created by default in the config file
and one should take extra care when changing those entries.


.. autopydantic_model:: HABApp.config.models.application.ApplicationConfig

Directories
--------------------------------------

.. autopydantic_model:: HABApp.config.models.directories.DirectoriesConfig
   :exclude-members: create_folders

Location
--------------------------------------

.. autopydantic_model:: HABApp.config.models.location.LocationConfig




MQTT
--------------------------------------
.. py:currentmodule:: HABApp.config.models.mqtt

.. autopydantic_model:: MqttConfig

Connection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: Connection

TLS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: TLSSettings

Subscribe
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: Subscribe

Publish
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: Publish

General
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: General




Openhab
--------------------------------------
.. py:currentmodule:: HABApp.config.models.openhab

.. autopydantic_model:: OpenhabConfig


.. _CONFIG_OPENHAB_CONNECTION:

Connection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: Connection

.. autopydantic_model:: Websocket

.. autopydantic_model:: WebsocketEventFilter


Ping
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: Ping

General
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: General





HABApp
--------------------------------------
.. py:currentmodule:: HABApp.config.models.habapp

.. autopydantic_model:: HABAppConfig

ThreadPool
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ThreadPoolConfig

Logging
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: LoggingConfig

Debug
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: DebugConfig

.. autopydantic_model:: PeriodicTracebackDumpConfig

.. autopydantic_model:: WatchEventLoopConfig
