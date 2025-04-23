# Tools

This directory contains some helpful tools for working with HABApp and openHAB

## prettify_json

Small tool to load and prettify print the json-in-json which are often emitted in openHAB events

## openhab_runner

This is a tool that makes it easy to run openHAB.
Different openHAB versions can be configured and a prompt in the beginning
asks which version should be started.
It supports starting additional processes, configuring the JAVA version per openHAB instance,
file synchronisation prior to starting openHAB and deleting logfiles.

If no path to configuration file is provided a configuration file in the ``run``
folder is created and/or used.

Should be run in the HABApp venv:

```text
python -m /path_to_habapp_folder/tools/openhab_runner
```

### Configuration

The tool supports wildcards in the configuration file.
All wildcards and the corresponding values are logged at startup.
Relative paths are relative to the configuration file.

It's possible do define global `sync` and `tasks` values which run always and 
before the `sync` and `tasks` values for an installation.


#### installations

Config which installations should be available. The name is shown in the prompt.

Example:
````yaml
- name: openhab 4.2
  path: ./path/Openhab/Installations/4.2/   # <-- path to openHAB installation 
  java: /path/to/Java/jdk17.0.6_10          # <-- path to java installation

  # --- optional and can be omitted, will only run when this installation is selected ---
  sync: []
  tasks:
    on_start: []
    on_close: []
  ````

#### sync

The `sync` section defines which file operations should be performed before / after running openHAB.
All files are copied from the source to the destination.

There is a ``test_sync`` flag in the config which only tests the sync operations but does not perform them.

Options for mode:
- `MERGE`: does not remove any files/folder in the destination folder
- `REMOVE_FILES`: remove all files in the destination folder, but keep folders
- `REMOVE_FILES_AND_FOLDERS`: remove all files and folders in the destination folder

Example:
````yaml
src: './conf_testing/lib/openhab'
dst: '%openhab_conf%'
mode: REMOVE_FILES
````

#### tasks

The `tasks` section defines which tasks should be started before / after running openHAB.
The tasks in on_start are started before openHAB and the tasks in on_close are started after openHAB is run.
With `wait: false` the task is started in the background and killed when all tasks are finished.
The task entries map directly to the corresponding fields from the python docs.

````yaml
name: 'Task Name'
cmd: 'Task Command'

# --- optional ---
args: [additional, args]
env: {additional: 'environment variables'}
cwd: working directory
timeout: 30 # How long to wait for the task to finish

# --- optional flags ---
shell: False         # run the command in a shell
wait: True           # wait for the task to finish or run in background/parallel
new_console: False   # run in new console
````
