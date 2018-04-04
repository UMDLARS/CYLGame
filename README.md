# Installing

**If you are looking for a game to play or want to make a game you should check out this repo instead: [https://github.com/UMDCYL/applehunt](https://github.com/UMDCYL/applehunt)**

## Dependencies

If you don't have python 3.6 on your system then you should install it.
For Ubuntu 16.04 and 14.04 run:
```
sudo add-apt-repository ppa:jonathonf/python-3.6
sudo apt-get update
sudo apt-get install python3.6 python3.6-dev
```

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
