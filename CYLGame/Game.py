import tcod
import tdl
import tempfile
import os.path
import random
import string
import sys

TCOT_ROOT_CONSOLE = None
TDL_ROOT_CONSOLE = None

# From: http://stackoverflow.com/a/2267446/4441526
digs = string.digits + string.letters
def int2base(x, base):
    if x < 0:
        sign = -1
    elif x == 0:
        return digs[0]
    else:
        sign = 1

    x *= sign
    digits = []

    while x:
        digits.append(digs[x % base])
        x /= base

    if sign < 0:
        digits.append('-')

    digits.reverse()

    return ''.join(digits)


def average(scores):
    return float((sum(scores) * 100) / len(scores)) / 100


def data_file(filename):
    resource_path = os.path.join(os.path.split(__file__)[0], os.path.pardir, "data", filename)
    return resource_path


class GameLanguage(object):
    LITTLEPY = 0

    @staticmethod
    def get_language_description(language):
        if language == GameLanguage.LITTLEPY:
            return open(data_file("little_python_intro.md")).read()

class Player(object):
    """
    Player base class. Requires the following attributes be initialized by the game maker:
    prog = LPProg
    """
    def run_program(self):
        try:
            old_state = self.get_state()
            new_state = self.prog.run(old_state)
            self.update_state(new_state)
        except AttributeError:
            print("Player class not properly initialized before running program!")

    def get_state(self):
        raise Exception("Not implemented!")

    def update_state(self, new_state):
        raise Exception("Not implemented!")

class DefaultPlayer(Player):
    def __init__(self, prog, move_consts, move_names, game):
        self.state = {}
        self.prog = prog # type: LPProg
        self.debug_vars = []
        self.move_consts = move_consts
        self.move_names = move_names
        # need this to get the player's state
        self.game = game

    def get_state(self):
        v = dict(self.state)
        v.update(self.move_consts)
        v.update(self.game.get_vars_for_bot())
        return v

    def update_state(self, new_state):
        for key in self.move_consts:
            new_state.pop(key)
        self.state = new_state
        human_vars = {}
        for v in self.state:
            if self.state[v] in self.move_names:
                human_vars[v] = self.move_names[self.state[v]] + " ("+str(self.state[v])+")"
            elif str(self.state[v]) == str(True):
                human_vars[v] = 1
            elif str(self.state[v]) == str(False):
                human_vars[v] = 0
            else:
                human_vars[v] = self.state[v]
        self.add_debug_vars([human_vars])

    def add_debug_vars(self, debug_vars):
        self.debug_vars.append(debug_vars)

    def get_debug_vars(self):
        return self.debug_vars


class Game(object):
    WEBONLY = True
    SCREEN_WIDTH = 0
    SCREEN_HEIGHT = 0
    GAME_TITLE = ""

    def is_running(self):
        """This is how the game runner knows if the game is over.

        Returns:
            bool: True if the game should still be play. False otherwise
        """
        raise Exception("Not implemented!")

    def create_new_player(self, prog):
        """This creates a new oject that inherits from the Player class.

        Returns:
            An object that inherets from the Player class with the given program.
        """
        raise Exception("Not implemented!")

    def get_debug_vars(self):
        raise Exception("Not implemented!")

    def do_turn(self):
        raise Exception("Not implemented!")

    def get_frame(self):
        raise Exception("Not implemented!")

    def init_board(self):
        raise Exception("Not implemented!")

    @staticmethod
    def default_prog_for_bot(language):
        raise Exception("Not implemented!")

    @staticmethod
    def get_intro():
        raise Exception("Not implemented!")

class NonGridGame(Game):
    WEBONLY = True

    def read_bot_state(self, state):
        raise Exception("Not Implemented!")

    def get_vars_for_bot(self):
        raise Exception("Not Implemented!")


class GridGame(Game):
    WEBONLY = False
    SCREEN_WIDTH = 80
    SCREEN_HEIGHT = 25
    CHAR_WIDTH = 8
    CHAR_HEIGHT = 8
    GAME_TITLE = ""
    CHAR_SET = data_file("fonts/terminal8x8_gs_ro.png")
    MOVE_CONSTS = {"north": ord("w"), "south": ord("s"), "west": ord("a"), "east": ord("d"),
                "northeast": ord("e"), "southeast": ord("c"), "northwest": ord("q"), "southwest": ord("z")}
    MOVE_NAMES = {ord("w"): "North", ord("s"): "South", ord("a"): "West", ord("d"): "East",
                ord("e"): "Northeast", ord("c"): "Southeast", ord("q"): "Northwest",
                ord("z"): "Southwest"}

    def handle_key(self, key):
        """This is where your game should react to user input.
        We have decided on some standards for input. The following are the standard chars and their meaning:
            Q:  Quit, you should do whatever you need to before the game ends. Probably set a flag so the draw_screen
                function can draw an end of game screen.
            w:  North or Up
            a:  West or Left
            d:  East or Right
            s:  South or Down
            q:  Northwest
            e:  Northeast
            z:  Southwest
            c:  Southeast

        Args:
            key (str): key is a string of length one repenting a key press.
        """
        raise Exception("Not implemented!")

    def draw_screen(self, libtcod, console):
        raise Exception("Not implemented!")

    def get_vars_for_bot(self):
        raise Exception("Not implemented!")

    def get_score(self):
        """This is the game runner gets the ending or mid-game score

        Returns:
            int: The current score.
        """
        raise Exception("Not implemented!")

    def create_new_player(self, prog):
        """Maybe we should force this to be implemented by the game maker, but that 
        would mean we have to update all of our current games... Just make a default for now.
        """
        # only support one player for GridGame right now
        self.player = DefaultPlayer(prog, self.MOVE_CONSTS, self.MOVE_NAMES, self)
        return self.player

    def init_board(self):
        global TDL_ROOT_CONSOLE
        if not TDL_ROOT_CONSOLE:
            TDL_ROOT_CONSOLE = tdl.init(0, 0)

        self.console = tdl.Console(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

    def do_turn(self, players):
        if len(players) > 1:
            raise Exception("This framework only supports on player!")

        next_vars = players[0].state
        if "move" in next_vars:
            self.handle_key(chr(next_vars["move"]))

    def get_debug_vars(self):
        return self.player.get_debug_vars()

    @staticmethod
    def get_screen_array(console):
        tf = tempfile.NamedTemporaryFile(mode="rb")
        tcod.console_save_asc(console.tcod_console, tf.name)
        data = tf.read()
        x, y = map(int, data.split("\n")[1].split())
        chars = "\n".join(data.split("\n")[2:])[1::9]
        arr = []
        for i in range(y):
            arr += [map(ord, chars[i::y])]
        return arr

    def get_frame(self):
        self.draw_screen(tcod, self.console.tcod_console)
        return self.get_screen_array(self.console)
        pass

    # leaving these in for backwards compatibility
    @staticmethod
    def get_move_consts():
        return {"north": ord("w"), "south": ord("s"), "west": ord("a"), "east": ord("d"),
                "northeast": ord("e"), "southeast": ord("c"), "northwest": ord("q"), "southwest": ord("z")}

    @staticmethod
    def get_move_names():
        return {ord("w"): "North", ord("s"): "South", ord("a"): "West", ord("d"): "East",
                ord("e"): "Northeast", ord("c"): "Southeast", ord("q"): "Northwest",
                ord("z"): "Southwest"}


class GameRunner(object):
    def __init__(self, game_class, progs=None):
        self.game_class = game_class  # type: type
        self.progs = None # type: list of LPProg
        if type(progs) is list:
            self.progs = progs  # type: LPProg
        elif progs:
            self.progs = [progs]

    def __run_for(self, score=False, playback=False, seed=None):
        assert self.progs is not None  # Make sure that we have a bot to run
        assert score != playback

        if not seed:
            seed = random.randint(0, sys.maxint)

        game = self.game_class(random.Random(seed))
        game.init_board()
        players = []
        for prog in self.progs:
            players.append(game.create_new_player(prog))

        if playback:
            screen_cap = []
            debug_vars = []

        while game.is_running():
            for player in players:
                player.run_program()
            if playback:
                screen_cap += [game.get_frame()]
            game.do_turn(players)

        if playback:
            return {"screen": screen_cap, "seed": int2base(seed, 36), "debug": game.get_debug_vars()}
        else:  # if score
            return game.get_score()

    def run_for_avg_score(self, times=1, seed=None, func=average):
        """Runs the given game keeping only the scores.

        Args:
            times (int): The number of times to run to get the average score.

        Return:
            The return value the average score for the times runs.
        """
        scores = []
        # TODO: make this able to run in a pool of threads (So it can be run on multiple CPUs)
        for t in range(times):
            scores += [self.__run_for(score=True, seed=seed)]
        return func(scores)

    def run_for_playback(self, seed=None):
        """Runs the given game saving the screen captures.

        Return:
            The return value is a 3-dimensional list the first dimension is time followed by y and x.
        """
        return self.__run_for(playback=True, seed=seed)

    def run(self, seed=None):
        """Will run the game for a user.

        Returns:
        """
        #TODO: abort if WEBONLY == True
        global TDL_ROOT_CONSOLE
        if not TDL_ROOT_CONSOLE:
            tdl.setFont(self.game_class.CHAR_SET)
            TDL_ROOT_CONSOLE = tdl.init(self.game_class.SCREEN_WIDTH, self.game_class.SCREEN_HEIGHT,
                                        self.game_class.GAME_TITLE)
        else:
            raise Exception("You are trying the run two games at the time! I cann't do that :(")

        game = self.game_class(random.Random(seed))
        console = tdl.Console(game.SCREEN_WIDTH, game.SCREEN_HEIGHT)
        while game.is_running():
            self.__run_user_turn(console, game)

    @staticmethod
    def get_screen_array(console):
        tf = tempfile.NamedTemporaryFile(mode="rb")
        tcod.console_save_asc(console.tcod_console, tf.name)
        data = tf.read()
        x, y = map(int, data.split("\n")[1].split())
        chars = "\n".join(data.split("\n")[2:])[1::9]
        arr = []
        for i in range(y):
            arr += [map(ord, chars[i::y])]
        return arr

    @staticmethod
    def __run_user_turn(console, game):
        game.draw_screen(tcod, console.tcod_console)
        TDL_ROOT_CONSOLE.blit(console, 0, 0, game.SCREEN_WIDTH, game.SCREEN_HEIGHT, 0, 0)
        tdl.flush()

        key = tdl.event.key_wait()
        if key.char:
            game.handle_key(key.char)


def run(game_class, avg_game_func=average):
    def serve(args):
        print("I am going to serve")
        from .Server import serve
        serve(game_class, host=args.host, port=args.port, game_data_path=args.dbfile, avg_game_func=avg_game_func)

    def play(args):
        print("Playing...")
        GameRunner(game_class).run(int(args.seed, 36))

    import argparse

    parser = argparse.ArgumentParser(prog=game_class.GAME_TITLE, description='Play ' + game_class.GAME_TITLE + '.')
    subparsers = parser.add_subparsers(help='What do you what to do?')
    parser_play = subparsers.add_parser('play', help='Play ' + game_class.GAME_TITLE + ' with a GUI')
    parser_play.add_argument('-s', '--seed', nargs="?", type=str, help='Manually set the random seed.',
                             default=int2base(random.randint(0, sys.maxint), 36))
    parser_play.set_defaults(func=play)
    parser_serve = subparsers.add_parser('serve', help='Serve ' + game_class.GAME_TITLE + ' to the web.')
    parser_serve.add_argument('-p', '--port', nargs="?", type=int, help='Port to serve on', default=5000)
    parser_serve.add_argument('-db', '--dbfile', nargs="?", type=str, help='The root path of the game database', default="temp_game")
    parser_serve.add_argument('--host', nargs="?", type=str, help='The mask to host to', default='127.0.0.1')
    parser_serve.set_defaults(func=serve)

    args = parser.parse_args()
    args.func(args)
