

==================================
Installation & Usage
==================================

----------------------------------
Virtual environment
----------------------------------

Installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. hint::
   HABApp requires at least Python 3.6
.. hint::
   On Windows use the ``python`` command instead of ``python3``

#. Navigate to the folder where the virtual environment shall be created (e.g.)::

    cd /opt

#. Create virtual environment (this will create a new folder "habapp")::

    python3 -m venv habapp

#. Go into folder of virtual environment::

    cd habapp

#. Activate the virtual environment

   Linux::

    source bin/activate

   Windows::

    Scripts\activate

#. Upgrade pip::

    python3 -m pip install --upgrade pip

#. Install HABApp::

    python3 -m pip install habapp

#. Run HABAp::

    habapp --config PATH_TO_CONFIGURATION_FOLDER

   If you use openHABian a good configuration folder would be ``/opt/openhab/conf/habapp`` because this is where your other configuration
   folders are located (e.g. the items and sitemaps folder). Just make sure to manually create the folder ``habapp`` before the start.



.. hint::
   After the installation take a look how to configure HABApp.
   A default configuration will be created on the first start.

Upgrading
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#. Stop HABApp

#. Run the following command::

    python3 -m pip install --upgrade habapp

#. Start HABApp

#. Observe the logs for errors in case there were changes


Error message while installing ujson
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Under windows the installation of ujson may throw the following error but the download link is not working.
Several working alternatives can be found `here <https://www.scivision.dev/python-windows-visual-c-14-required/>`_.

.. code-block:: none

  Running setup.py install for ujson ... error
    ERROR: Complete output from command 'C:\Users\User\Desktop\HABapp\habapp\Scripts\python.exe' -u -c 'import setuptools, tokenize;__file__='"'"'C:\\Users\\User\\AppData\\Local\\Temp\\pip-install-4y0tobjp\\ujson\\setup.py'"'"';f=getattr(tokenize, '"'"'open'"'"', open)(__file__);code=f.read().replace('"'"'\r\n'"'"', '"'"'\n'"'"');f.close();exec(compile(code, __file__, '"'"'exec'"'"'))' install --record 'C:\Users\User\AppData\Local\Temp\pip-record-6t2yo712\install-record.txt' --single-version-externally-managed --compile --install-headers 'C:\Users\User\Desktop\HABapp\habapp\include\site\python3.7\ujson':
    ERROR: Warning: 'classifiers' should be a list, got type 'filter'
    running install
    running build
    running build_ext
    building 'ujson' extension
    error: Microsoft Visual C++ 14.0 is required. Get it with "Microsoft Visual C++ Build Tools": https://visualstudio.microsoft.com/downloads/
    ----------------------------------------

Error message while installing ruamel.yaml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: none

  _ruamel_yaml.c:4:10: fatal error: Python.h: No such file or directory

Run the follwing command to fix it::

  sudo apt install python3-dev

Autostart after reboot
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Check where habapp is installed

    which habapp

To automatically start HABApp from the virtual environment after a reboot call::

    nano /etc/systemd/system/habapp.service


and copy paste the following contents. If the user which is running openhab is not "openhab" replace accordingly.
If your installation is not done in "/opt/habapp/bin" replace accordingly as well::

    [Unit]
    Description=HABApp
    After=network-online.target
    
    [Service]
    Type=simple
    User=openhab
    Group=openhab
    ExecStart=/opt/habapp/bin/habapp -c PATH_TO_CONFIGURATION_FOLDER
    
    [Install]
    WantedBy=multi-user.target

Press Ctrl + x to save.

Now execute the following commands to enable autostart::

    sudo systemctl --system daemon-reload
    sudo systemctl enable habapp.service

It is now possible to start, stop, restart and check the status of HABApp with::

    sudo systemctl start habapp.service
    sudo systemctl stop habapp.service
    sudo systemctl restart habapp.service
    sudo systemctl status habapp.service

----------------------------------
Docker
----------------------------------

Installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Installation through `docker <https://hub.docker.com/r/spacemanspiff2007/habapp>`_ is also available::

    docker pull spacemanspiff2007/habapp

To have the proper timestamps in the logs set the ``TZ`` environment variable of the container accordingly (e.g. ``TZ=Europe/Berlin``).


Updating docker on Synology
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To update your HABApp docker within Synology NAS, you just have to do the following:

On the Synology NAS just select "Download" with tag "latest" to download the new image.
It will overwrite the old one on the NAS.
Then stop the container. After selecting "Action" -> "Clear" on the HABapp container, the container is there, but without any content.
After starting the container again, everything should immediately work again.

----------------------------------
Upgrading to a newer version
----------------------------------

It is recommended to upgrade the installation on another machine. Configure your production instance in the configuration
and set the ``listen_only`` switch(es) in the configuration to ``True``. Observe the logs for any errors.
This way if there were any breaking changes rules can easily be fixed before problems occur on the running installation.

----------------------------------
HABApp arguments
----------------------------------

.. execute_code::
    :header_code: Execute habapp with "-h" to view possible command line arguments

    # skip
    habapp -h
    # skip

    # hide
    import HABApp.__main__
    HABApp.__main__.get_command_line_args(['-h'])
    # hide


