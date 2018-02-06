from __future__ import division
import os.path
import random
import string
import sys

from CYLGame.Frame import GridFrameBuffer
from CYLGame.Player import UserProg

FPS = 30


# From: http://stackoverflow.com/a/2267446/4441526
digs = string.digits + string.ascii_letters
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
        x //= base

    if sign < 0:
        digits.append('-')

    digits.reverse()

    return ''.join(digits)


def scorer(func):
    """This function is a decorator for a scoring function.
       This is hack a to get around self being passed as the first argument to the scoring function."""
    def wrapped(a, b=None):
        if b is not None:
            return func(b)
        return func(a)
    return wrapped


@scorer
def average(scores):
    return float((sum(scores) * 100) / len(scores)) / 100


def data_file(filename):
    resource_path = os.path.join(os.path.split(__file__)[0], "data", filename)
    return resource_path


class GameLanguage(object):
    LITTLEPY = 0

    @staticmethod
    def get_language_description(language):
        if language == GameLanguage.LITTLEPY:
            return open(data_file("little_python_intro.md")).read()


class Game(object):
    WEBONLY = True
    SCREEN_WIDTH = 0
    SCREEN_HEIGHT = 0
    GAME_TITLE = ""
    OPTIONS = None
    MULTIPLAYER = False  # TODO: document
    TURN_BASED = False  # TODO: document

    def is_running(self):
        """This is how the game runner knows if the game is over.

        Returns:
            bool: True if the game should still be play. False otherwise
        """
        raise Exception("Not implemented!")

    def create_new_player(self, prog):
        """This creates n new objects that inherits from the Player class.

        Returns:
            n new objects that inherit from the Player class with the given program.
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
    def default_prog_for_computer():
        """This method is only for multi-player games to implement.
        Returns:
            type[Prog]
        """
        raise Exception("Not implemented!")

    @staticmethod
    def get_intro():
        raise Exception("Not implemented!")

    @staticmethod
    def get_move_consts():
        return ConstMapping()

    @staticmethod
    def get_number_of_players():
        """This method is only for multi-player games to implement.
        Returns:
            int: The number of players needed to play the game.
        """
        raise Exception("Not implemented!")


class NonGridGame(Game):
    WEBONLY = True
    GRID = False

    def read_bot_state(self, state):
        raise Exception("Not Implemented!")

    def get_vars_for_bot(self):
        raise Exception("Not Implemented!")


class ConstMapping(dict):
    def __init__(self, seq=None, **kwargs):
        """
        dict() -> new empty dictionary
        dict(mapping) -> new dictionary initialized from a mapping object's
            (key, value) pairs
        dict(iterable) -> new dictionary initialized as if via:
            d = {}
            for k, v in iterable:
                d[k] = v
        dict(**kwargs) -> new dictionary initialized with the name=value pairs
            in the keyword argument list.  For example:  dict(one=1, two=2)
        # (copied from class doc)
        """
        super(ConstMapping, self).__init__()
        if isinstance(seq, dict):
            for v, k in seq.items():
                self[v] = k
        elif kwargs:
            for v, k in kwargs:
                self[v] = k
        else:
            for v, k in seq:
                self[v] = k

    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        if value in self:
            del self[value]
        dict.__setitem__(self, key, value)
        dict.__setitem__(self, value, key)

    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)

    def __len__(self):
        return dict.__len__(self) // 2


class GridGame(Game):
    WEBONLY = False
    GRID = True
    SCREEN_WIDTH = 80
    SCREEN_HEIGHT = 25
    CHAR_WIDTH = 8
    CHAR_HEIGHT = 8
    GAME_TITLE = ""
    CHAR_SET = data_file("fonts/terminal8x8_gs_ro.png")
    __frame_buffer = None

    def is_running(self):
        """This is how the game runner knows if the game is over.

        Returns:
            bool: True if the game should still be play. False otherwise
        """
        raise Exception("Not implemented!")

    def create_new_player(self, prog):  # TODO: add option to create computer, user or bot players.
        """ TODO: write this
        """
        raise Exception("Not Implemented!")

    def do_turn(self):
        """This function should read the new state of all the players and react to them."""
        raise Exception("Not implemented!")

    def draw_screen(self, frame_buffer):
        """WARNING: There MUST NOT be any game logic in this function since it isn't called when simulating the game
                    during the competitions.
        """
        raise Exception("Not implemented!")

    def get_frame(self):
        if self.__frame_buffer is None:
            self.__frame_buffer = GridFrameBuffer(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.draw_screen(self.__frame_buffer)
        return self.__frame_buffer.dump()

    def get_vars(self, player):
        """ TODO: write this
        """
        raise Exception("Not implemented!")

    def get_score(self):
        """This is the game runner gets the ending or mid-game score

        Returns:
            int: The current score.
        """
        raise Exception("Not implemented!")

    @staticmethod
    def default_prog_for_bot(language):
        raise Exception("Not implemented!")

    @staticmethod
    def get_intro():
        raise Exception("Not implemented!")

    @staticmethod
    def get_move_consts():
        return ConstMapping({"north": ord("w"), "south": ord("s"), "west": ord("a"), "east": ord("d"),
                "northeast": ord("e"), "southeast": ord("c"), "northwest": ord("q"), "southwest": ord("z")})


class GameRunner(object):
    def __init__(self, game_class, room=None):
        self.game_class = game_class  # type: Type[Game]
        self.user_is_playing = False
        if room is None:
            self.user_is_playing = True
        else:
            self.room = room  # type: Room
        self.players = []

    def __run_for(self, score=False, playback=False, seed=None):
        assert len(self.room.bots) > 0  # Make sure that we have a bot to run
        assert score != playback

        if not seed:
            seed = random.randint(0, sys.maxsize)
        game = self.game_class(random.Random(seed))

        game.init_board()
        self.players = []
        for bot in self.room.bots:
            # TODO: This is a hack. Remove me sometime.
            if not hasattr(bot, "options"):
                bot.options = {}
            if playback:
                bot.options["debug"] = True

            self.players += [game.create_new_player(bot)]

        screen_cap = []
        if game.TURN_BASED:
            self.current_player = 0
        while game.is_running():
            if playback:
                screen_cap += [game.get_frame()]

            players = self.players
            if game.TURN_BASED:
                players = [self.players[self.current_player]]
                self.current_player = (self.current_player + 1) % len(self.players)
                # TODO: sync screen cap and debug vars.

            for player in players:
                player.run_turn(game.random)

            game.do_turn()

        if playback:
            self.room.set_playback(screen_cap)
            for player in self.players:
                self.room.set_bot_debug(player.prog, player.debug_vars)
            return {"seed": int2base(seed, 36)}
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
        # This import statement is here so pygame is only imported if needed.
        from CYLGame import Display
        game = self.game_class(random.Random(seed))

        charset = Display.CharSet(self.game_class.CHAR_SET, self.game_class.CHAR_WIDTH, self.game_class.CHAR_HEIGHT)
        display = Display.PyGameDisplay(*charset.char_size_to_pix((game.SCREEN_WIDTH, game.SCREEN_HEIGHT)), title=game.GAME_TITLE)

        clock = Display.get_clock()

        frame_buffer = GridFrameBuffer(*charset.pix_size_to_char(display.get_size()), charset=charset)
        frame_updated = True

        game.init_board()
        players = []
        if game.MULTIPLAYER:
            computer_bot_class = game.default_prog_for_computer()
            for _ in range(game.get_number_of_players() - 1):
                players += [game.create_new_player(computer_bot_class())]
        player = game.create_new_player(UserProg())

        while game.is_running():
            clock.tick(FPS)
            for key in display.get_keys():
                # TODO: fix
                player.prog.key = key
                player.run_turn()
                for comp_player in players:
                    comp_player.run_turn()
                game.do_turn()
                frame_updated = True

            if frame_updated:
                game.draw_screen(frame_buffer)
                display.update(frame_buffer)
                frame_updated = False


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
                             default=int2base(random.randint(0, sys.maxsize), 36))
    parser_play.set_defaults(func=play)
    parser_serve = subparsers.add_parser('serve', help='Serve ' + game_class.GAME_TITLE + ' to the web.')
    parser_serve.add_argument('-p', '--port', nargs="?", type=int, help='Port to serve on', default=5000)
    parser_serve.add_argument('-db', '--dbfile', nargs="?", type=str, help='The root path of the game database', default="temp_game")
    parser_serve.add_argument('--host', nargs="?", type=str, help='The mask to host to', default='127.0.0.1')
    parser_serve.set_defaults(func=serve)

    args = parser.parse_args()
    args.func(args)
