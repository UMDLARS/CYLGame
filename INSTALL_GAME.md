# Installing (and Playing) a Game

This document explains how to install and play a generic CYLGame game on a clean install of Ubuntu Linux. We will use the basic 'Applehunt' game, 
but if you wish to install a different CYLGame modules, replace the git repository and directories described
in this document with the appropriate values.

## Getting Started
### Install `python3.6` and `pip`

```
sudo add-apt-repository ppa:deadsnakes/ppa  # Only needed for Ubuntu 14.04 and 16.04
sudo apt-get update
sudo apt-get install python3-pip libssl-dev python3.6 python3.6-dev 
```

### Install `git`

```
sudo apt-get install git
```

### Install `pipenv`

```
sudo python3.6 -m pip install pipenv
```

### Clone the game repository (insert your game here)

```
git clone https://github.com/UMDLARS/applehunt.git     # or a different game of your choice
cd applehunt                                           # or the directory created in the previous line
pipenv install
```

### Running
From within the directory of the game in question (e.g., `applehunt`), run:

```
pipenv run python game.py serve
```
This will start the game running on an application web server on the `localhost` interface, which you can access by going to:

`http://localhost:5000`

... in your web browser.

To make this game server accessible from the Internet or other hosts, additional steps are required. We do this by forwarding a URL from our web frontend to the game server running at a particular IP and port (this can be on the same or a different machine). To specify the IP and port for the game server, use:

```
pipenv run python game.py serve --host IPADDRESS -p PORT -db GAME_DB
```

If you have any questions feel free to contact the devteam at <umdcyl-dev@d.umn.edu>

### Playing the Game On Screen

If you're developing or testing the game, you may want to play the game on your own monitor (rather than through the web interface). To do this, follow the above instructions, then:

```
$ pipenv install --dev
```

To play the game:

```
$ pipenv run python game.py play
```
