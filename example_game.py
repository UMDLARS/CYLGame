from __future__ import print_function
import sys
from CYLGameServer import serve
from CYLGameServer import CYLGameLanguage
from CYLGameServer import CYLGame


class TickTackToe(CYLGame):
    SCREEN_WIDTH = 80
    SCREEN_HEIGHT = 25
    LIMIT_FPS = 20
    GAME_TITLE = "Tick Tack Toe"

    def __init__(self):
        self.grid = [0] * 9
        self.player = 1
        self.ai = 2
        self.running = True
        self.draw_win = False
        self.centerx = self.SCREEN_WIDTH / 2
        self.centery = self.SCREEN_HEIGHT / 2

        self.d = 3

        self.width = 4

        self.offsetx = self.centerx - ((self.width * self.d) / 2)
        self.offsety = self.centery - ((self.width * self.d) / 2)

        self.grid_to_char = {1: "X", 2: "O"}
        self.tacks = []
        for i in range(self.d):
            for j in range(self.d):
                self.tacks += [((j * self.width) + self.offsetx, (i * self.width) + self.offsety)]

    def check_win(self):
        for i in range(3):
            if len(set(self.grid[i::3])) == 1 and self.grid[i]:
                return self.grid[i]
            if len(set(self.grid[i * 3:(i + 1) * 3])) == 1 and self.grid[i * 3]:
                return self.grid[i * 3]

        if len({self.grid[0], self.grid[4], self.grid[8]}) == 1 and self.grid[4]:
            return self.grid[4]
        if len({self.grid[2], self.grid[4], self.grid[6]}) == 1 and self.grid[4]:
            return self.grid[4]
        return 0

    def handle_key(self, key):
        is_valid = False
        if key.isdigit() and 0 < int(key) < 10:
            spot = int(key) - 1
            if not self.grid[spot]:
                self.grid[spot] = self.player
                is_valid = True
        if key == "Q":
            self.running = False
        if not is_valid:
            return False

        if self.check_win():
            self.draw_win = self.check_win()
            return True

        for i in range(9):
            if not self.grid[i]:
                self.grid[i] = self.ai
                break

        if self.check_win():
            self.draw_win = self.check_win()
            return True

        return True

    def is_running(self):
        return self.running

    def get_vars_for_bot(self):
        bot_vars = {}
        for i in range(9):
            bot_vars["spot" + str(i + 1)] = self.grid[i]
        return bot_vars

    @staticmethod
    def default_prog_for_bot(language):
        if language == CYLGameLanguage.LITTLEPY:
            return open("example_bot.lp", "r").read()

    def draw_screen(self, console):
        # libtcod.console_set_default_foreground(console, libtcod.white)
        console.set_colors((255,255,255), (0,0,0))
        for i in range(self.width * self.d - 1):
            for j in range(self.d - 1):
                x = self.offsetx + i - (self.width / 2) + 1
                y = (j * self.width) + self.offsety + (self.width / 2)
                ch = '-'
                console.draw_char(x, y, ch)
                # libtcod.console_put_char(console, x, y, ch, libtcod.BKGND_NONE)

        for i in range(self.d - 1):
            for j in range(self.width * self.d - 1):
                x = (i * self.width) + self.offsetx + (self.width / 2)
                y = self.offsety + j - (self.width / 2) + 1
                ch = '|'
                console.draw_char(x, y, ch)
                # libtcod.console_put_char(console, x, y, ch, libtcod.BKGND_NONE)

        for i in range(self.d - 1):
            for j in range(self.d - 1):
                x = (i * self.width) + self.offsetx + (self.width / 2)
                y = (j * self.width) + self.offsety + (self.width / 2)
                ch = '+'
                console.draw_char(x, y, ch)
                # libtcod.console_put_char(console, x, y, ch, libtcod.BKGND_NONE)

        for i in range(len(self.tacks)):
            t = self.tacks[i]
            if self.grid[i]:
                console.draw_char(t[0], t[1], self.grid_to_char[self.grid[i]])
                # libtcod.console_put_char(console, t[0], t[1], self.grid_to_char[self.grid[i]], libtcod.BKGND_NONE)
            else:
                console.draw_char(t[0], t[1], str(i + 1))
                # libtcod.console_put_char(console, t[0], t[1], str(i + 1), libtcod.BKGND_NONE)

        if self.draw_win:
            message = ""
            if self.draw_win == self.player:
                message = "You win!!!"
            elif self.draw_win == self.ai:
                message = "You lose :("

            for i in range(len(message)):
                ch = message[i]
                y = self.centery + ((self.width * self.d)/2)
                x = self.centerx - (len(message)/2) + i - 1
                console.draw_char(x, y, ch)
                # libtcod.console_put_char(console, x, y, ch, libtcod.BKGND_NONE)
            self.running = False


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("Run: python game.py serve\nTo start web server.\nRun: python game.py play\n To play on this computer.")
    if sys.argv[1] == "serve":
        serve(TickTackToe)
    elif sys.argv[1] == "play":
        from CYLGameServer import CYLGameRunner
        CYLGameRunner(TickTackToe).run()
