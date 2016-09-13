import tdl

TDL_ROOT_CONSOLE = None


class CYLGameLanguage(object):
    LITTLEPY = 0


class CYLGame(object):
    SCREEN_WIDTH = 80
    SCREEN_HEIGHT = 25
    LIMIT_FPS = 20

    def is_running(self):
        pass

    def get_vars_for_bot(self):
        pass

    @staticmethod
    def default_prog_for_bot(language):
        pass

    def handle_key(self, key):
        pass

    def draw_screen(self, console):
        pass


class CYLGameRunner(object):
    def __init__(self, game_class, bot=None):
        self.game = game_class()
        self.bot = bot
        self.console = None

        self.kill = False

        self.key_consts = {"A": 65}
        for i in range(10):
            self.key_consts["NUM" + str(i)] = ord(str(i))

    def run(self):
        global TDL_ROOT_CONSOLE
        self.kill = False
        if not self.bot:
            if not TDL_ROOT_CONSOLE:
                TDL_ROOT_CONSOLE = tdl.init(self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT, 'python/libtcod tick-tack-toe')
            tdl.set_fps(self.game.LIMIT_FPS)
        else:
            if not TDL_ROOT_CONSOLE:
                TDL_ROOT_CONSOLE = tdl.init(0, 0)
            tdl.set_fps(self.game.LIMIT_FPS)

        self.console = tdl.Console(self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT)
        self.screen_cap = []
        while self.game.is_running() and not self.kill:
            if self.bot:
                self.__run_bot()
            else:
                self.__run_user()
        if self.bot:
            return self.screen_cap

    def get_screen_array(self):
        arr = []
        for j in range(self.game.SCREEN_HEIGHT):
            arr += [[]]
            for i in range(self.game.SCREEN_WIDTH):
                char = self.console.get_char(i, j)[0]
                arr[j] += [char]
        return arr

    def __run_user(self):
        self.game.draw_screen(self.console)
        TDL_ROOT_CONSOLE.blit(self.console, 0, 0, self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT,0,0)
        tdl.flush()

        key = tdl.event.key_wait()
        if key.char:
            c = key.char
            self.game.handle_key(c)

    def __run_bot(self):
        self.game.draw_screen(self.console)
        self.screen_cap += [self.get_screen_array()]

        vars = self.game.get_vars_for_bot()
        vars.update(self.key_consts)
        ending_state = self.bot.run(vars)

        if "move" in ending_state:
            is_valid = self.game.handle_key(chr(ending_state["move"]))
            if not is_valid:
                self.kill = True
        else:
            self.kill = True
