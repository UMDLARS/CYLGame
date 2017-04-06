import os.path
import random
import string
import sys

from CYLGame.Frame import GridFrameBuffer
from CYLGame.Player import UserProg

FPS = 30


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
    resource_path = os.path.join(os.path.split(__file__)[0], os.path.pardir, "data", filename)
    return resource_path


class GameLanguage(object):
    LITTLEPY = 0

    @staticmethod
    def get_language_description(language):
        if language == GameLanguage.LITTLEPY:
            return open(data_file("little_python_intro.md")).read()


class NonGridGame(object):
    WEBONLY = True

    def read_bot_state(self, state):
        raise Exception("Not Implemented!")

    def get_vars_for_bot(self):
        raise Exception("Not Implemented!")


class Game(object):
    WEBONLY = False
    SCREEN_WIDTH = 80
    SCREEN_HEIGHT = 25
    CHAR_WIDTH = 8
    CHAR_HEIGHT = 8
    GAME_TITLE = ""
    CHAR_SET = data_file("fonts/terminal8x8_gs_ro.png")
    TURN_BASED = False  # TODO: document
    MULTIPLAYER = False  # TODO: document

    def is_running(self):
        """This is how the game runner knows if the game is over.

        Returns:
            bool: True if the game should still be play. False otherwise
        """
        raise Exception("Not implemented!")

    def get_new_player(self, prog):  # TODO: add option to create computer, user or bot players.
        """ TODO: write this
        """
        raise Exception("Not Implemented!")

    def update(self):
        """This function should move all of the players."""
        raise Exception("Not implemented!")

    def draw_screen(self, frame_buffer):
        raise Exception("Not implemented!")

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
        return {"north": ord("w"), "south": ord("s"), "west": ord("a"), "east": ord("d"),
                "northeast": ord("e"), "southeast": ord("c"), "northwest": ord("q"), "southwest": ord("z")}

    @staticmethod
    def get_move_names():
        return {ord("w"): "North", ord("s"): "South", ord("a"): "West", ord("d"): "East",
                ord("e"): "Northeast", ord("c"): "Southeast", ord("q"): "Northwest",
                ord("z"): "Southwest"}

    @staticmethod
    def get_number_of_players():
        """This method is only for multi-player games to implement.
        Returns:
            int: The number of players needed to play the game.
        """
        raise Exception("Not implemented!")


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


class GameRunner(object):
    def __init__(self, game_class, room=None):
        self.game_class = game_class  # type: Type[Game]
        self.user_is_playing = False
        if room is None:
            self.user_is_playing = True
        else:
            self.room = room  # type: Room
        self.players = []

        self.BOT_CONSTS = self.game_class.get_move_consts()
        self.CONST_NAMES = self.game_class.get_move_names()

    def __run_for(self, score=False, playback=False, seed=None):
        assert len(self.room.bots) > 0  # Make sure that we have a bot to run
        assert score != playback

        if not seed:
            seed = random.randint(0, sys.maxsize)
        game = self.game_class(random.Random(seed))

        self.players = []
        for bot in self.room.bots:
            self.players += [game.get_new_player(bot)]

        framebuffer = GridFrameBuffer(game.SCREEN_WIDTH, game.SCREEN_HEIGHT)
        if playback:
            screen_cap = []
            for player in self.players:
                player.debug_vars = []
        if game.TURN_BASED:
            self.current_player = 0
        vars = {}
        while game.is_running():
            screen = self.__run_next_turn(framebuffer, game, playback=playback)
            if screen and playback:
                screen_cap += [screen]
            else:
                break

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
        """
        # This import statement is here so pygame is only imported if needed.
        from CYLGame import Display
        game = self.game_class(random.Random(seed))

        charset = Display.CharSet(self.game_class.CHAR_SET, self.game_class.CHAR_WIDTH, self.game_class.CHAR_HEIGHT)
        display = Display.PyGameDisplay(*charset.char_size_to_pix((game.SCREEN_WIDTH, game.SCREEN_HEIGHT)), title=game.GAME_TITLE)

        clock = Display.get_clock()

        frame_buffer = GridFrameBuffer(*charset.pix_size_to_char(display.get_size()), charset=charset)
        frame_updated = True

        player = game.get_new_player(UserProg())

        while game.is_running():
            clock.tick(FPS)
            for key in display.get_keys():
                # TODO: fix
                player.prog.key = key
                player.make_move(None)
                game.update()
                frame_updated = True

            if frame_updated:
                game.draw_screen(frame_buffer)
                display.update(frame_buffer)
                frame_updated = False

    def __run_next_turn(self, framebuffer, game, playback=True):
        """run_bot will do a single bot turn"""
        # if prev_vars is None:
        #     prev_vars = dict()
        game.draw_screen(framebuffer)
        if playback:
            screen_cap = framebuffer.dump()
        else:
            screen_cap = None

        players = self.players
        if game.TURN_BASED:
            players = [self.players[self.current_player]]
            self.current_player = (self.current_player + 1) % len(self.players)
            # TODO: sync screen cap and debug vars.

        for player in players:
            vars = dict(player.prev_vars)
            vars.update(self.BOT_CONSTS)
            vars.update(game.get_vars(player))
            nxt_vars = player.make_move(vars)

            # remove consts
            for key in self.BOT_CONSTS:
                nxt_vars.pop(key)

            player.prev_vars = nxt_vars
            if playback:
                human_vars = {}
                for name, val in nxt_vars.items():
                    if val in self.CONST_NAMES:
                        human_vars[name] = self.CONST_NAMES[val] + " (" + str(val) + ")"
                    elif str(val) == str(True):
                        human_vars[name] = 1
                    elif str(val) == str(False):
                        human_vars[name] = 0
                    else:
                        human_vars[name] = val
                player.debug_vars += [human_vars]

        game.update()

        return screen_cap


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
