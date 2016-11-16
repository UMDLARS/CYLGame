#!/usr/bin/python
from apple_game import AppleFinder
from littlepython import Compiler
from CYLGame.Database import GameDB
from CYLGame.Comp import sim_competition


comp_token = "PB253836D"
game = AppleFinder
compiler = Compiler()
gamedb = GameDB("temp_game")

sim_competition(compiler=compiler, game=game, gamedb=gamedb, token=comp_token, runs=100, debug=True)