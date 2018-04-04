# Installing (and Playing) a Game

This document explains how to install and play a generic CYLGame game on a clean install of Ubuntu Linux. We will use the basic 'Applehunt' game, 
but if you wish to install a different CYLGame modules, replace the git repository and directories described
in this document with the appropriate values.

## Getting Started
### Install `python3.6` and `pip`

```
sudo apt-get install python3-pip libssl-dev
sudo add-apt-repository ppa:jonathonf/python-3.6
sudo apt-get update
sudo apt-get install python3.6 python3.6-dev 
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

To make this game server accessible from the Internet or other hosts, additional steps are required. If you'd like to do this, or if you have any questions feel free to contact the devteam at <umdcyl-dev@d.umn.edu>
