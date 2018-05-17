from __future__ import division
import os.path
import random
import sys

from CYLGame.Frame import GridFrameBuffer
from CYLGame.Player import UserProg
from CYLGame.Utils import int2base

FPS = 30


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

    def start_game(self):
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


class ConstMapping:
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
        self.name_to_val_mapping = {}
        self.val_to_name_mapping = {}
        if isinstance(seq, dict):
            for v, k in seq.items():
                self[v] = k
        elif kwargs:
            for v, k in kwargs:
                self[v] = k
        else:
            for v, k in seq:
                self[v] = k

    def update(self, other):
        for var, val in other.items():
            self[var] = val

    @property
    def names(self):
        return self.name_to_val_mapping.keys()

    @property
    def values(self):
        return self.name_to_val_mapping.values()

    def __iter__(self):
        return iter(self.name_to_val_mapping.items())

    def __contains__(self, item):
        return item in self.name_to_val_mapping or item in self.val_to_name_mapping

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.name_to_val_mapping[item]
        elif isinstance(item, int):
            return self.val_to_name_mapping[item]
        raise TypeError()

    def __setitem__(self, key, value):
        # TODO: assert key is a valid littlepython variable name.
        assert isinstance(key, str), "Key must be a variable name"
        assert isinstance(value, int), "Only valid value is an int currently"

        if key in self.name_to_val_mapping:
            old_value = self.name_to_val_mapping[key]
            del self.name_to_val_mapping[key]
            del self.val_to_name_mapping[old_value]
        assert value not in self.val_to_name_mapping, "This is a one-to-one mapping"

        self.name_to_val_mapping[key] = value
        self.val_to_name_mapping[value] = key

    def __delitem__(self, key):
        value = self.name_to_val_mapping[key]
        del self.name_to_val_mapping[key]
        del self.val_to_name_mapping[value]

    def __len__(self):
        return len(self.name_to_val_mapping)


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
    def __init__(self, game_class):
        self.game_class = game_class  # type: Type[Game]

    def run(self, room, playback=True):
        """The the game.

        Args:
            room(Room): The room to play.
            playback(bool): if True save the playback.

        Returns:
            Room:
        """
        assert len(room.bots) > 0  # Make sure that we have a bot to run

        game = self.game_class(random.Random(room.seed))

        game.init_board()
        players = []
        for bot in room.bots:
            # TODO: This is a hack. Remove me sometime.
            if not hasattr(bot, "options"):
                bot.options = {}
            if playback:
                bot.options["debug"] = True

            players += [game.create_new_player(bot)]

        game.start_game()

        screen_cap = []
        if game.TURN_BASED:
            current_player = 0
        while game.is_running():
            if playback:
                screen_cap += [game.get_frame()]

            players = players
            if game.TURN_BASED:
                players = [players[current_player]]
                current_player = (current_player + 1) % len(players)
                # TODO: sync screen cap and debug vars.

            for player in players:
                player.run_turn(game.random)

            game.do_turn()

        room.score = game.get_score()
        if playback:
            room.screen_cap = screen_cap
            for player in players:
                room.debug_vars[player.prog] = player.debug_vars

        return room

    def run_for_avg_score(self, room, times=1, func=average):
        """Runs the given game keeping only the scores.

        Args:
            times (int): The number of times to run to get the average score.

        Return:
            The return value the average score for the times runs.
        """
        # TODO: replace this method with a better one.
        scores = []
        for t in range(times):
            scores += [self.run(room.rand_seeded).score]
        return func(scores)

    def run_with_local_display(self, seed=None):
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

        game.start_game()

        while game.is_running():
            clock.tick(FPS)
            for key in display.get_keys():
                # TODO: fix
                player.prog.key = key
                player.run_turn(game.random)
                for comp_player in players:
                    comp_player.run_turn(game.random)
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
        reuse_addr = True
        if args.no_addr_reuse:
            reuse_addr = None
        serve(game_class, host=args.host, port=args.port, game_data_path=args.dbfile, avg_game_func=avg_game_func,
              debug=args.debug, multiplayer_scoring_interval=args.scoring_time, reuse_addr=reuse_addr)

    def play(args):
        print("Playing...")
        GameRunner(game_class).run_with_local_display(int(args.seed, 36))

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
    parser_serve.add_argument('--no-addr-reuse', action='store_true')
    parser_serve.add_argument('--debug', action='store_true')
    parser_serve.add_argument('-s', '--scoring_time', nargs="?", type=int, help='The number of seconds between re-scoring all the bots.', default=60)
    parser_serve.set_defaults(func=serve)

    args = parser.parse_args()
    args.func(args)
