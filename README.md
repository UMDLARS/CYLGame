# Installing

## Dependencies

### Standalone
 - pygame

**Ubuntu install command**
```sudo apt-get install python-dev python-pip && sudo -H pip install -U pygame```

**Mac OS install command**
```sudo easy_install pip && sudo -H pip install -U pygame```

### Server
Add ```sudo -H``` to this command if needed.
Python:
```
pip install -U flask flask-compress flask_classful Flask-Markdown ujson littlepython msgpack gevent
```

## Setup
Clone this repo and add the path to the repo to your path variable.

Ex. export PYTHONPATH=$PYTHONPATH:/path/to/add/CYLGame

## Play a game
Go here and download the repo: [https://github.com/UMDCYL/applehunt](https://github.com/UMDCYL/applehunt)
To play run:
```
python apple_game.py play
```
