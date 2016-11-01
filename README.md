# Installing

## Dependencies

### Standalone
Linux: libsdl1.2, python-dev
Ubuntu install command
```sudo apt-get install python-dev python-pip libsdl1.2debian python-cffi libffi-dev libsdl1.2-dev && sudo -H pip install -U cffi tdl libtcod-cffi```

### Server
Add ```sudo -H``` to this command if needed.
Python:
```
pip install flask flask-compress Flask-Markdown ujson littlepython
```

## Setup
Clone this repo and add the path to the repo to your path variable.

Ex. export PYTHONPATH=$PYTHONPATH:/path/to/add/CYLGameServer

## Serve a game
Find a game repo and clone it then run:
```
python game.py serve
```

# TODO
 - Figure out how to do sensors.
 - Add real time playing from web.
