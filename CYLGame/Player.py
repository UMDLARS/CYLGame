import random
import sys
import traceback
from abc import ABC, abstractmethod

from littlepython import Compiler, ExecutionCountExceededException
from littlepython.error import LittlePythonBaseExcetion

from CYLGame.Utils import int2base


# A template class for the Prog for the Player.
class Prog(object):
    def __init__(self):
        # The `options`, `token` and `name` attributes are reserved for the GameRunner
        self.options = {}
        self.token = None
        self.name = None

    def run(self, state=None, max_op_count=-1, random=None):
        pass


class LittlePythonProg(Prog):
    def __init__(self, prog, name="Computer"):
        super().__init__()
        self.prog = Compiler().compile(prog)
        self.name = name

    def run(self, *args, **kargs):
        return self.prog.run(*args, **kargs)


class UserProg(Prog):
    def __init__(self):
        super().__init__()
        self.name = "You"
        self.key = None

    def run(self, *args, **kwargs):
        return {"move": ord(self.key)}


class Player(ABC):
    def __init__(self, prog):
        self.prog = prog
        self.prev_vars = {}
        self.debugging = prog.options.get("debug", False)
        self.debug_vars = []  # TODO: Maybe make this into a class.
        self.running = True

    def run_turn(self, random, max_ops=1000000):
        if self.running:
            try:
                nxt_state = self.prog.run(self.get_state(), max_op_count=max_ops, random=random)
                self.update_state(dict(nxt_state))
                self.prev_vars = nxt_state
            except LittlePythonBaseExcetion as e:
                print("Player class raised: {}!".format(e.__class__.__name__))
                self.running = False
                self.prev_vars = {}

    @abstractmethod
    def get_state(self):
        pass

    @abstractmethod
    def update_state(self, new_state):
        pass


class DefaultGridPlayer(Player):
    """Make sure that all bot_vars are updated in game.do_turn"""
    def __init__(self, prog, bot_consts):
        """
        Args:
             prog(Prog):
             bot_consts(ConstMapping):
        """
        super(DefaultGridPlayer, self).__init__(prog)
        self.bot_consts = bot_consts
        self.bot_vars = {}
        self.move = None

    def get_state(self):
        state = dict(self.prev_vars)
        state.update(self.bot_consts)
        state.update(self.bot_vars)
        return state

    def update_state(self, state):
        # remove consts
        for key in self.bot_consts.names:
            state.pop(key, None)

        self.move = chr(state.get("move", ord("Q")))

        if self.debugging:
            human_vars = {}
            for name, val in state.items():
                if isinstance(val, int) and val in self.bot_consts:
                    human_vars[name] = self.bot_consts[val] + " (" + str(val) + ")"
                elif str(val) == str(True):
                    human_vars[name] = 1
                elif str(val) == str(False):
                    human_vars[name] = 0
                else:
                    human_vars[name] = val
            self.debug_vars += [human_vars]


class Room(object):
    def __init__(self, bots=None, seed=None):
        self.bots = bots
        if bots is None:
            self.bots = []

        self.seed = seed
        if seed is None:
            self.seed = random.randint(0, sys.maxsize)

        self.debug_vars = {}
        self.screen_cap = None

    def save(self, gamedb):
        """The method saves the game data to a new game. Note: this room must be run before calling this function.

        Args:
            gamedb (GameDB): The current game database.

        Returns: The gtoken of the newly created game.

        """
        if self.screen_cap is None:
            raise Exception("You must run this room before trying to save it.")
        game_data = {"screen": self.screen_cap,
                     "seed": int2base(self.seed, 36)}
        player_data = {}
        for player in self.bots:
            if hasattr(player, "token") and player.token is not None:
                player_data[player.token] = self.debug_vars[player]
        return gamedb.add_new_game(game_data, per_player_data=player_data)

    @property
    def rand_seeded(self):
        """A randomly seeded room with the same bots."""
        return Room(self.bots)

    def __str__(self):
        return "<Room with '{}'>".format("', '".join(map(lambda x: x.name, self.bots)))
