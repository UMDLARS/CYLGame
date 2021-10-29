from typing import List, Optional

import sys
from abc import ABC, abstractmethod
from random import Random, randint

from littlepython.error import LittlePythonBaseExcetion
from littlepython.interpreter import LPProg

# A template class for the Prog for the Player.
from CYLGame.structures.const_mapping import ConstMapping
from CYLGame.Utils import int2base


class Prog(ABC):
    def __init__(
        self, options: dict, token: Optional[str] = None, name: Optional[str] = None, code_hash: Optional[str] = None
    ):
        # The `options`, `token` and `name` attributes are reserved for the GameRunner
        self.options = options
        self.token = token
        self.name = name
        self.code_hash = code_hash

    @abstractmethod
    def run(self, state: dict, max_op_count: int = -1, random=None):
        pass


class LittlePythonProg(Prog):
    def __init__(
        self,
        prog: LPProg,
        options: dict,
        token: Optional[str] = None,
        name: Optional[str] = None,
        code_hash: Optional[str] = None,
    ):
        super().__init__(options=options, token=token, name=name, code_hash=code_hash)
        self.prog = prog

    def run(self, *args, **kargs):
        return self.prog.run(*args, **kargs)


class UserProg(Prog):
    def __init__(self):
        super().__init__(name="You", options={})
        self.key = None

    def run(self, *args, **kwargs):
        return {"move": ord(self.key)}


class Player(ABC):
    def __init__(self, prog: Prog):
        self.prog = prog
        self.prev_vars: dict = {}
        self.debugging = prog.options.get("debug", False)
        self.debug_vars: list = []  # TODO: Maybe make this into a class.
        self.running = True

    def run_turn(self, random: Random, max_ops: int = 1000000):
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
    def get_state(self) -> dict:
        pass

    @abstractmethod
    def update_state(self, new_state: dict):
        pass


class DefaultGridPlayer(Player):
    """Make sure that all bot_vars are updated in game.do_turn"""

    def __init__(self, prog: Prog, bot_consts: ConstMapping):
        super(DefaultGridPlayer, self).__init__(prog)
        self.bot_consts = bot_consts
        self.bot_vars: dict = {}
        self.move: Optional[str] = None

    def get_state(self) -> dict:
        state = dict(self.prev_vars)
        state.update(self.bot_consts)
        state.update(self.bot_vars)
        return state

    def update_state(self, state: dict):
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
    def __init__(self, bots: List[Prog] = None, seed=None):
        self.bots = bots
        if bots is None:
            self.bots = []

        self.seed = seed
        if seed is None:
            self.seed = randint(0, sys.maxsize)

        self.debug_vars: dict = {}
        self.screen_cap = None

    def save(self, gamedb):
        """The method saves the game data to a new game. Note: this room must be run before calling this function.

        Args:
            gamedb (GameDB): The current game database.

        Returns: The gtoken of the newly created game.

        """
        if self.screen_cap is None:
            raise Exception("You must run this room before trying to save it.")
        game_data = {"screen": self.screen_cap, "seed": int2base(self.seed, 36)}
        player_data = {}
        for player in self.bots:
            if hasattr(player, "token") and player.token is not None:
                player_data[player.token] = {"debug_vars": self.debug_vars[player], "code_hash": player.code_hash}
        return gamedb.add_new_game(game_data, per_player_data=player_data)

    @property
    def rand_seeded(self):
        """A randomly seeded room with the same bots."""
        return Room(self.bots)

    def __str__(self):
        return "<Room with '{}'>".format("', '".join(map(lambda x: x.name, self.bots)))
