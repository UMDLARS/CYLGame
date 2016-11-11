import tcod
import tdl
import tempfile
import os.path

TCOT_ROOT_CONSOLE = None
TDL_ROOT_CONSOLE = None


def data_file(filename):
    resource_path = os.path.join(os.path.split(__file__)[0], os.path.pardir, "data", filename)
    return resource_path


class GameLanguage(object):
    LITTLEPY = 0

    @staticmethod
    def get_language_description(language):
        if language == GameLanguage.LITTLEPY:
            return open(data_file("little_python_intro.md")).read()


class Game(object):
    SCREEN_WIDTH = 80
    SCREEN_HEIGHT = 25
    CHAR_WIDTH = 8
    CHAR_HEIGHT = 8
    GAME_TITLE = ""
    CHAR_SET = data_file("fonts/terminal8x8_gs_ro.png")

    def is_running(self):
        """This is how the game runner knows if the game is over.

        Returns:
            bool: True if the game should still be play. False otherwise
        """
        raise Exception("Not implemented!")

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

    @staticmethod
    def default_prog_for_bot(language):
        raise Exception("Not implemented!")


class GameRunner(object):
    def __init__(self, game_class, bot=None):
        self.game_class = game_class  # type: type
        self.bot = bot  # type: LPProg

        keys = [chr(x) for x in range(ord("A"), ord("Z") + 1)] + \
               [chr(x) for x in range(ord("a"), ord("z") + 1)] + \
               [chr(x) for x in range(ord("0"), ord("9") + 1)]

        key_consts = {}
        for c in keys:
            key_consts["key_" + c] = ord(c)

        dir_consts = {"north": ord("w"), "south": ord("s"), "west": ord("a"), "east": ord("d")}

        self.BOT_CONSTS = {}
        self.BOT_CONSTS.update(key_consts)
        self.BOT_CONSTS.update(dir_consts)

    def __run_for(self, score=False, playback=False):
        global TDL_ROOT_CONSOLE
        assert self.bot is not None  # Make sure that we have a bot to run
        assert score != playback

        if not TDL_ROOT_CONSOLE:
            TDL_ROOT_CONSOLE = tdl.init(0, 0)

        game = self.game_class()

        console = tdl.Console(game.SCREEN_WIDTH, game.SCREEN_HEIGHT)
        if playback:
            screen_cap = []
        vars = {}
        while game.is_running():
            result = self.__run_bot_turn(console, game, vars, capture_screen=playback)
            if result:
                vars, screen = result
                if playback:
                    screen_cap += [screen]
            else:
                break

        if playback:
            return screen_cap
        else:  # if score
            return game.get_score()

    def run_for_avg_score(self, times=1):
        """Runs the given game keeping only the scores.

        Args:
            times (int): The number of times to run to get the average score.

        Return:
            The return value the average score for the times runs.
        """
        scores = []
        # TODO: make this able to run in a pool of threads (So it can be run on multiple CPUs)
        for t in range(times):
            scores += [self.__run_for(score=True)]
        return sum(scores) / times

    def run_for_playback(self):
        """Runs the given game saving the screen captures.

        Return:
            The return value is a 3-dimensional list the first dimension is time followed by y and x.
        """
        return self.__run_for(playback=True)

    def run(self):
        """Will run the game for a user.

        Returns:
        """
        global TDL_ROOT_CONSOLE
        if not TDL_ROOT_CONSOLE:
            tdl.setFont(self.game_class.CHAR_SET)
            TDL_ROOT_CONSOLE = tdl.init(self.game_class.SCREEN_WIDTH, self.game_class.SCREEN_HEIGHT,
                                        self.game_class.GAME_TITLE)
        else:
            raise Exception("You are trying the run two games at the time! I cann't do that :(")

        game = self.game_class()
        console = tdl.Console(game.SCREEN_WIDTH, game.SCREEN_HEIGHT)
        while game.is_running():
            self.__run_user_turn(console, game)

    @staticmethod
    def get_screen_array(console):
        tf = tempfile.NamedTemporaryFile(mode="rb")
        tcod.console_save_asc(console.tcod_console, tf.name)
        lines = tf.readlines()
        y, x = map(int, lines[1].split())
        chars = lines[2][1::9]
        arr = []
        for i in range(y):
            arr += [map(ord, chars[i::x])]
        return arr

    @staticmethod
    def __run_user_turn(console, game):
        game.draw_screen(tcod, console.tcod_console)
        TDL_ROOT_CONSOLE.blit(console, 0, 0, game.SCREEN_WIDTH, game.SCREEN_HEIGHT, 0, 0)
        tdl.flush()

        key = tdl.event.key_wait()
        if key.char:
            game.handle_key(key.char)

    def __run_bot_turn(self, console, game, prev_vars={}, capture_screen=True):
        """run_bot will do a single bot turn"""
        game.draw_screen(tcod, console.tcod_console)
        if capture_screen:
            screen_cap = self.get_screen_array(console)
        else:
            screen_cap = None

        vars = dict(prev_vars)
        vars.update(self.BOT_CONSTS)
        vars.update(game.get_vars_for_bot())
        nxt_vars = self.bot.run(vars)

        if "move" in nxt_vars:
            game.handle_key(chr(nxt_vars["move"]))
        else:
            return False
        return nxt_vars, screen_cap


def run(game_class):
    def serve(args):
        from .Server import serve
        serve(game_class, host=args.host, port=args.port)
        print("I am going to serve")

    def play(args):
        print("Playing...")
        GameRunner(game_class).run()

    import argparse

    parser = argparse.ArgumentParser(prog="Apple Hunt", description='Play Apple Hunt.')
    subparsers = parser.add_subparsers(help='What do you what to do?')
    parser_play = subparsers.add_parser('play', help='Play Apple Hunt with a GUI')
    parser_play.set_defaults(func=play)
    parser_serve = subparsers.add_parser('serve', help='Serve Apple Hunt to the web.')
    parser_serve.add_argument('-p', '--port', nargs="?", type=int, help='Port to serve on', default=5000)
    parser_serve.add_argument('--host', nargs="?", type=str, help='The mask to host to', default='127.0.0.1')
    parser_serve.set_defaults(func=serve)

    args = parser.parse_args()
    args.func(args)
