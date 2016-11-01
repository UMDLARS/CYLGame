# Installing

## Dependencies

### Standalone
 - libsdl1.2
 - cffi
 - tdl
 - libtcod-cffi

**Ubuntu install command**
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

## Play a game
Go here and download the repo: [https://github.umn.edu/UMDCYL/applegame](https://github.umn.edu/UMDCYL/applegame)
To play run:
```
python apple_game.py play
```
