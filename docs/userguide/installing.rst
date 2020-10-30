Installing (and Playing) a Game
===============================

This document explains how to install and play a generic CYLGame game on
a clean install of Ubuntu Linux. We will use the basic ‘Applehunt’ game,
but if you wish to install a different CYLGame modules, replace the git
repository and directories described in this document with the
appropriate values.

Getting Started
---------------

Install ``git``
~~~~~~~~~~~~~~~

::

   sudo apt-get install git

Install ``pyenv``
~~~~~~~~~~~~~~~~~

::

   curl https://pyenv.run | bash  # Don't forget to follow the instructions to add commands to your rc file.
   exec $SHELL
   pyenv update


Install Python Build dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Go to https://github.com/pyenv/pyenv/wiki#suggested-build-environment and find
the commands to install the needed dependencies. For Ubuntu this is the following command.

::

   sudo apt-get update; sudo apt-get install --no-install-recommends make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

Install Python
~~~~~~~~~~~~~~

First you should figure out which version of python you need. (It is fine if
you don't want to figure this out, just skip to the below commands and use
version ``3.8``.) To find the needed python version checkout the ``Pipfile``
inside the game's repository to figure out the version of python needed (It
will be in the format of ``python_version = "X.Y"``).
Note that you can install as many versions of python as you would like so don't
worry about conflicting versions across games. If you need a different version
for a new game run the following commands again for the needed version (or
pipenv will ask to do it for you).

::

   pyenv isntall --list | less  # use this to find the latest micro version of the python you want.
   pyenv install X.Y.Z  # where X.Y are the "major.minor" version require and Z is the latest mirco version.


Install ``pipenv``
~~~~~~~~~~~~~~~~~~

This step you only have to do with first version you install.

::

   pyenv global X.Y.Z  # you only need to do this once
   python3 --version   # Should print out the version you just installed.
   python3 -m pip install pipenv
   exec $SHELL

Clone the game repository (insert your game here)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   git clone https://github.com/UMDLARS/applehunt.git     # or a different game of your choice
   cd applehunt                                           # or the directory created in the previous line
   pipenv install

.. note::
   If you didn't install the needed version of python pipenv should display a
   message like: ``Warning: Python X.Y was not found on your system...``
   followed by ``Would you like us to install CPython X.Y.Z with Pyenv?
   [Y/n]:``. Answer ``y`` otherwise you will need to manually install the
   correct python version.

Running a Game Server on Localhost
~~~~~~~

From within the directory of the game in question (e.g., ``applehunt``),
run:

::

   pipenv run python game.py serve

This will start the game running on an application web server on the
``localhost`` interface, which you can access by going to:

``http://localhost:5000``

… in your web browser.

To make this game server accessible from the Internet or other hosts,
additional steps are required. We do this by forwarding a URL from our
web frontend to the game server running at a particular IP and port
(this can be on the same or a different machine). To specify the IP and
port for the game server, use:

::

   pipenv run python game.py serve --host IPADDRESS -p PORT -db GAME_DB

If you have any questions feel free to contact the devteam at
umdcyl-dev@d.umn.edu

Playing the Game On Screen
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you’re developing or testing the game, you may want to play the game
on your own monitor (rather than through the web interface). To do this,
follow the above instructions, then:

::

   $ sudo apt-get install python3-pygame
   $ pipenv install --dev

To play the game:

::

   $ pipenv run python game.py play
