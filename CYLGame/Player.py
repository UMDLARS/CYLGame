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

    def run_turn(self):
        try:
            nxt_state = self.prog.run(self.get_state())
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

    def get_state(self):
        state = dict(self.prev_vars)
        state.update(self.bot_consts)
        state.update(self.bot_vars)
        return state

    def update_state(self, state):
        # remove consts
        for key in self.bot_consts:
            state.pop(key, None)

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


# class Player(object):
#     """
#     Player base class. Requires the following attributes be initialized by the game maker:
#     prog = LPProg
#     """
#     def run_program(self):
#         try:
#             old_state = self.get_state()
#             new_state = self.prog.run(old_state)
#             self.update_state(new_state)
#         except (AttributeError, TypeError):
#             traceback.print_exc(file=sys.stdout)
#             #print old_state
#             print("Player class not properly initialized before running program!")
#
#     def get_state(self):
#         raise Exception("Not implemented!")
#
#     def update_state(self, new_state):
#         raise Exception("Not implemented!")
#
#
# class DefaultPlayer(Player):
#     def __init__(self, prog, move_consts, move_names, game):
#         self.state = {}
#         self.prog = prog # type: LPProg
#         self.debug_vars = []
#         self.move_consts = move_consts
#         self.move_names = move_names
#         # need this to get the player's state
#         self.game = game
#
#     def get_state(self):
#         v = dict(self.state)
#         v.update(self.move_consts)
#         v.update(self.game.get_vars_for_bot())
#         return v
#
#     def update_state(self, new_state):
#         for key in self.move_consts:
#             new_state.pop(key)
#         self.state = new_state
#         human_vars = {}
#         for v in self.state:
#             if self.state[v] in self.move_names:
#                 human_vars[v] = self.move_names[self.state[v]] + " ("+str(self.state[v])+")"
#             elif str(self.state[v]) == str(True):
#                 human_vars[v] = 1
#             elif str(self.state[v]) == str(False):
#                 human_vars[v] = 0
#             else:
#                 human_vars[v] = self.state[v]
#         self.add_debug_vars([human_vars])
#
#     def add_debug_vars(self, debug_vars):
#         self.debug_vars.append(debug_vars)
#
#     def get_debug_vars(self):
#         return self.debug_vars


# vars = dict(player.prev_vars)
# vars.update(self.BOT_CONSTS)
# vars.update(game.get_vars(player))
# nxt_vars = player.make_move(vars)
#
# # remove consts
# for key in self.BOT_CONSTS:
#     nxt_vars.pop(key)
#
# player.prev_vars = nxt_vars
# if playback:
#     human_vars = {}
#     for name, val in nxt_vars.items():
#         if val in self.CONST_NAMES:
#             human_vars[name] = self.CONST_NAMES[val] + " (" + str(val) + ")"
#         elif str(val) == str(True):
#             human_vars[name] = 1
#         elif str(val) == str(False):
#             human_vars[name] = 0
#         else:
#             human_vars[name] = val
#     player.debug_vars += [human_vars]
