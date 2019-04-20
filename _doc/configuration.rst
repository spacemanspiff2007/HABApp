

Configuration
==================================
Configuration is done through `config.yml` The parent folder of the file can be specified with `-c PATH` or `--config PATH`.
If nothing is specified the file `config.yml` is searched in the subdirectory `HABApp` in

* the current working directory
* the venv directory
* the user home

If the config does not yet exist in the folder a blank configuration will be created


Configuration contents
------------------------------
.. code-block:: yaml
    
    directories:
        logging: log    # If the filename for the logfile in logging.yml is not absolute it will be placed in this directory
        rules: rules    # All *.py files in this folder (and subfolders) will be loaded
        lib: lib        # Custom modules, libraries and files can be placed there
    
    openhab:
        ping:
            enabled: true        # If enabled the configured item will show how long it takes to send an update from HABApp
                                 # and get the updated value back in milliseconds
            item: 'HABApp_Ping'  # Name of the item
            interval: 10         # Seconds between two pings
        connection:
            host: localhost
            port: 8080
            user: ''
            password: ''
        general:
            listen_only: False  # If True  HABApp will not change any value on the openhab instance.
                                # Useful for testing rules from another machine.
   
    mqtt:
        connection:
            client_id: HABApp
            host: ''
            port: 8883
            user: ''
            password: ''
            tls: true
            tls_insecure: false  # do not check certificate
        
        subscribe:         # Changes to Subscribe get picked up without restarting HABApp
            qos: 0         # Default QoS for subscribing
            topics:
            - '#'          # Subscribe to this topic
            - 0            # QoS for previous topic, can be omitted
        
        publish:
            qos: 0          # Default QoS when publishing values
            retain: false   # Default retain flag when publishing values
