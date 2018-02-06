import sys
import traceback


# A template class for the Prog for the Player.
class Prog(object):
    def __init__(self):
        # The `options` attribute is reserved for the GameRunner
        self.options = {}

    def run(self, state=None, max_op_count=-1):
        pass


class UserProg(Prog):
    def __init__(self):
        self.key = None
        self.options = {}

    def run(self, *args, **kwargs):
        return {"move": ord(self.key)}


class Player(object):
    def __init__(self, prog):
        self.prog = prog
        self.prev_vars = {}
        self.debugging = prog.options.get("debug", False)
        self.debug_vars = []  # TODO: Maybe make this into a class.

    def run_turn(self, random, max_ops=1000000):
        try:
            nxt_state = self.prog.run(self.get_state(), max_op_count=max_ops, random=random)
            self.update_state(dict(nxt_state))
            self.prev_vars = nxt_state
        except:
            traceback.print_exc(file=sys.stdout)
            print("Player class had an error!")
            self.update_state({})  # if the program had an error pass an empty state.
            self.prev_vars = {}

    def get_state(self):
        raise Exception("Not implemented!")


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
        for key in self.bot_consts:
            state.pop(key, None)

        self.move = chr(state.get("move", ord("Q")))

        if self.debugging:
            human_vars = {}
            for name, val in state.items():
                if val in self.bot_consts:
                    human_vars[name] = self.bot_consts[val] + " (" + str(val) + ")"
                elif str(val) == str(True):
                    human_vars[name] = 1
                elif str(val) == str(False):
                    human_vars[name] = 0
                else:
                    human_vars[name] = val
            self.debug_vars += [human_vars]


class Room(object):
    def __init__(self, bots=None):
        if bots is None:
            self.bots = []
        else:
            self.bots = bots

        self.debug_vars = {}
        self.screen_cap = None

    def set_bot_debug(self, bot, debug_vars):
        self.debug_vars[bot] = debug_vars

    def set_playback(self, screen_cap):
        self.screen_cap = screen_cap
