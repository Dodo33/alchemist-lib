Install
=======


Installing requirements
-----------------------

Lets install python3 and mysql.

GNU/Linux
~~~~~~~~~

First of all to make sure that everything is up to date, let’s update and upgrade the system with apt-get.
::
    $ sudo apt-get update
    $ sudo apt-get -y upgrade
    
Probably python3 is already installed so let's check.
::
    
    $ python3 -V

If the command above returns something like ``Python 3.5.2`` it's all ok. Otherwise install python with the following command.
::
    $ sudo apt-get install python3

To manage software packages for Python, let’s install pip.
::
    $ sudo apt-get install -y python3-pip

A more detailed guide can be found on `Digital Ocean <https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-ubuntu-16-04>`_.

Installing MySQL can be done by runnung the following command.
::
    $ sudo apt-get install mysql-server

The MySQL/Python connector can be installed with:
::
    $ sudo apt-get install python3-mysql.connector
    

Installing alchemist_lib
------------------------

Installing with ``pip``:
~~~~~~~~~~~~~~~~~~~~~~~~
If `python3-pip <https://en.wikipedia.org/wiki/Pip_(package_manager)>`_ is already installed::
        
    $ sudo pip3 install alchemist_lib
    $ sudo pip3 install git+https://github.com/femtotrader/pandas_talib.git
    $ sudo pip3 install https://github.com/s4w3d0ff/python-poloniex/archive/v0.4.7.zip
        
If you don't have pip installed, you can easily install it by downloading and running `get-pip.py <https://bootstrap.pypa.io/get-pip.py>`_.
    
Cloning the repository with ``git``:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If `git <https://en.wikipedia.org/wiki/Git>`_ is already installed::
        
    $ git clone https://github.com/Dodo33/alchemist-lib
    $ cd alchemist-lib
    $ python3 setup.py install
    
    $ sudo pip3 install git+https://github.com/femtotrader/pandas_talib.git
    $ sudo pip3 install https://github.com/s4w3d0ff/python-poloniex/archive/v0.4.7.zip


Important
---------

After the installation it's important to specify mysql credentials::

    $ sudo alchemist populate -l "hostname" -u "username" -p "password" -d "database_name"

