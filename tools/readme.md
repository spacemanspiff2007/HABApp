# Tools

This directory contains some helpful tools for working with HABApp and openHAB

## openhab_runner

This is a tool that allows running openHAB.
Different openHAB versions can be configured and a prompt in the beginning
asks which version should be started.
It supports starting processes, configuring the JAVA version per openHAB instance,
file synchronisation prior to starting openHAB and deleting logfiles.

If no path to configuration file is provided a configuration file in the ``run``
folder is created and/or used.

Should be run in the HABApp venv:

```text
python -m /path_to_habapp_folder/tools/openhab_runner
```

## prettify_json

Small tool to load and prettiy print the json-in-json which are often emitted in openHAB events
