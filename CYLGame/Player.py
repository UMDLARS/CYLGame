

# A template class for the Prog for the Player.
class Prog(object):
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
