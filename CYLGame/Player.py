

# A template class for the Prog for the Player.
class Prog(object):
    # The `options` attribute is reserved for the GameRunner
    def run(self, static_vars=None, max_op_count=-1):
        pass


class UserProg(Prog):
    def __init__(self):
        self.key = None

    def run(self, *args, **kwargs):
        return {"move": self.key}


class Player(object):
    def __init__(self, prog):
        self.prog = prog
        self.prev_vars = {}
        self.debug_vars = None

    def make_move(self, state):
        nxt_state = self.prog.run(state)
        self.handle_move(dict(nxt_state))
        return nxt_state

    def handle_move(self, state):
        raise Exception("Not Implemented!")


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