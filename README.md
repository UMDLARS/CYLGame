# Installing

## Dependencies

### Standalone
 - libsdl1.2
 - cffi
 - libtcod-cffi
 - tdl

**Ubuntu install command**
```sudo apt-get install python-dev python-pip libsdl1.2debian python-cffi libffi-dev libsdl1.2-dev && sudo -H pip install -U cffi libtcod-cffi tdl```

**Mac OS install command**
```sudo easy_install pip && sudo -H pip install -U cffi libtcod-cffi tdl```

### Server
Add ```sudo -H``` to this command if needed.
Python:
```
pip install flask flask-compress flask_classful Flask-Markdown ujson littlepython
```

## Setup
Clone this repo and add the path to the repo to your path variable.

Ex. export PYTHONPATH=$PYTHONPATH:/path/to/add/CYLGame

## Play a game
Go here and download the repo: [https://github.umn.edu/UMDCYL/applegame](https://github.umn.edu/UMDCYL/applegame)
To play run:
```
python apple_game.py play
```
