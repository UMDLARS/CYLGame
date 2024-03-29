from __future__ import division

from typing import List, Optional, Type

import os.path
import random
import sys
from dataclasses import dataclass
from pathlib import Path

from CYLGame.Frame import GridFrameBuffer
from CYLGame.Player import Player, UserProg
from CYLGame.Sprite import SpriteSet
from CYLGame.structures.const_mapping import ConstMapping
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
    OPTIONS: Optional[str] = None
    MULTIPLAYER = False  # TODO: document

    def __init__(self, random):
        self.random = random

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
    __frame_buffer = None

    def is_running(self):
        """This is how the game runner knows if the game is over.

        Returns:
            bool: True if the game should still be play. False otherwise
        """
        raise Exception("Not implemented!")

    def create_new_player(self, prog):  # TODO: add option to create computer, user or bot players.
        """TODO: write this"""
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
            self.__frame_buffer = GridFrameBuffer(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, charset=self.get_sprite_set())
        self.draw_screen(self.__frame_buffer)
        return self.__frame_buffer.dump()

    def get_vars(self, player):
        """TODO: write this"""
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
        return ConstMapping(
            {
                "north": ord("w"),
                "south": ord("s"),
                "west": ord("a"),
                "east": ord("d"),
                "northeast": ord("e"),
                "southeast": ord("c"),
                "northwest": ord("q"),
                "southwest": ord("z"),
            }
        )

    @classmethod
    def get_sprite_set(cls) -> SpriteSet:
        return SpriteSet(
            char_width=cls.CHAR_WIDTH,
            char_height=cls.CHAR_HEIGHT,
            char_rows=16,
            char_columns=16,
            image_filepath=Path(cls.CHAR_SET),
        )


@dataclass
class PlayGameState:
    game: Game
    computer_players: List[Player]
    human_player: Player
    human_prog: UserProg
    seed: int

    moves: str
    frame: Optional[List[List[int]]]


class GameRunner(object):
    def __init__(self, game_class: Type[Game]):
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
        while game.is_running():
            if playback:
                screen_cap += [game.get_frame()]

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
        assert isinstance(game, GridGame)

        charset = Display.CharSet.from_sprite_set(game.get_sprite_set())
        display = Display.PyGameDisplay(
            *charset.char_size_to_pix((game.SCREEN_WIDTH, game.SCREEN_HEIGHT)), title=game.GAME_TITLE
        )

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

    def init_game(self, seed: int) -> PlayGameState:
        game = self.game_class(random.Random(seed))

        game.init_board()
        players = []
        if game.MULTIPLAYER:
            computer_bot_class = game.default_prog_for_computer()
            for _ in range(game.get_number_of_players() - 1):
                players += [game.create_new_player(computer_bot_class())]
        user_prog = UserProg()
        player = game.create_new_player(user_prog)

        game.start_game()
        return PlayGameState(
            game=game,
            computer_players=players,
            human_player=player,
            human_prog=user_prog,
            seed=seed,
            moves="",
            frame=game.get_frame(),
        )

    @staticmethod
    def move_game(state: PlayGameState, move: str) -> PlayGameState:
        player, comp_players = state.human_player, state.computer_players
        local_random = state.game.random
        game = state.game
        human_prog = state.human_prog

        human_prog.key = move
        player.run_turn(local_random)
        for comp_player in state.computer_players:
            comp_player.run_turn(local_random)
        game.do_turn()
        state.frame = game.get_frame()

        if game.is_running():
            state.moves += move

        return state


def run(game_class, avg_game_func=average):
    def serve(args):
        print("I am going to serve")
        from .Server import serve

        reuse_addr = True
        if args.no_addr_reuse:
            reuse_addr = None
        serve(
            game_class,
            host=args.host,
            port=args.port,
            game_data_path=args.dbfile,
            avg_game_func=avg_game_func,
            debug=args.debug,
            multiplayer_scoring_interval=args.scoring_time,
            reuse_addr=reuse_addr,
        )

    def play(args):
        print("Playing...")
        GameRunner(game_class).run_with_local_display(int(args.seed, 36))

    import argparse

    parser = argparse.ArgumentParser(prog=game_class.GAME_TITLE, description="Play " + game_class.GAME_TITLE + ".")
    subparsers = parser.add_subparsers(help="What do you what to do?")
    subparsers.required = True
    subparsers.dest = "command"
    parser_play = subparsers.add_parser("play", help="Play " + game_class.GAME_TITLE + " with a GUI")
    parser_play.add_argument(
        "-s",
        "--seed",
        nargs="?",
        type=str,
        help="Manually set the random seed.",
        default=int2base(random.randint(0, sys.maxsize), 36),
    )
    parser_play.set_defaults(func=play)
    parser_serve = subparsers.add_parser("serve", help="Serve " + game_class.GAME_TITLE + " to the web.")
    parser_serve.add_argument("-p", "--port", nargs="?", type=int, help="Port to serve on", default=5000)
    parser_serve.add_argument(
        "-db", "--dbfile", nargs="?", type=str, help="The root path of the game database", default="temp_game"
    )
    parser_serve.add_argument(
        "--debug-log",
        nargs="?",
        type=str,
        help="The file path to use for the debug log."
        '"{dbname}" in the path will be replaced by the path to the game database',
        default="{dbfile}/log/debug.log",
    )
    parser_serve.add_argument(
        "--error-log",
        nargs="?",
        type=str,
        help="The file path to use for the error log."
        '"{dbname}" in the path will be replaced by the path to the game database',
        default="{dbfile}/log/error.log",
    )
    parser_serve.add_argument("--host", nargs="?", type=str, help="The mask to host to", default="127.0.0.1")
    parser_serve.add_argument("--no-addr-reuse", action="store_true")
    parser_serve.add_argument("--debug", action="store_true")
    parser_serve.add_argument(
        "-s",
        "--scoring_time",
        nargs="?",
        type=int,
        help="The number of seconds between re-scoring all the bots.",
        default=60,
    )
    parser_serve.set_defaults(func=serve)

    args = parser.parse_args()
    args.func(args)
