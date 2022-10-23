from pathlib import Path

from CYLGame.Frame import GridFrameBuffer
from CYLGame.Game import ConstMapping, GridGame
from CYLGame.Player import DefaultGridPlayer
from CYLGame.Sprite import SpriteSet, TwoDimensionalSpriteColoring


def replace(i, old_color, new_color):
    img = i.load()
    for y in range(i.size[1]):
        for x in range(i.size[0]):
            if img[x, y] == old_color:
                img[x, y] = new_color


class TwoDCustomCharSize(GridGame):
    SCREEN_WIDTH = 40
    SCREEN_HEIGHT = 20
    SPRITE_SET = None

    @staticmethod
    def get_intro():
        return "Test"

    @staticmethod
    def default_prog_for_bot(_):
        return ""

    @classmethod
    def get_sprite_set(cls) -> SpriteSet:
        if not cls.SPRITE_SET:
            coloring = TwoDimensionalSpriteColoring(
                base_sprite_set=SpriteSet(
                    char_width=16,
                    char_height=16,
                    char_rows=16,
                    char_columns=16,
                    image_filepath=Path("resources/terminal16x16_gs_ro.png"),
                ),
                foreground_mapping={"green": (0, 255, 0)},
                background_mapping={"water": (0, 0, 255), "dirt": (150, 75, 0)},
            )
            cls.GREEN = coloring.get_foreground_value("green")
            cls.WATER = coloring.get_background_value("water")
            cls.DIRT = coloring.get_background_value("dirt")
            cls.SPRITE_SET = coloring.sprite_set
        return cls.SPRITE_SET

    def __init__(self, random):
        super().__init__(random)
        self.running = True

    def init_board(self):
        pass

    def create_new_player(self, prog):
        self.player = DefaultGridPlayer(prog, ConstMapping({}))
        return self.player

    def start_game(self):
        pass

    def is_running(self):
        return self.running

    def draw_screen(self, frame_buffer: GridFrameBuffer):
        frame_buffer.set(2, 1, 0)
        frame_buffer.set(3, 1, 1)
        frame_buffer.set(4, 1, 2)
        frame_buffer.set(2, 2, 3)
        frame_buffer.set(3, 2, 4)
        frame_buffer.set(4, 2, 5)
        frame_buffer.set(2, 3, ord("A") + self.GREEN)
        frame_buffer.set(2, 4, ord("A") + self.WATER)
        frame_buffer.set(3, 3, ord("Q") + self.WATER)
        frame_buffer.set(4, 3, ord("a") + self.GREEN + self.WATER)
        frame_buffer.set(5, 3, ord("W") + self.DIRT + self.GREEN)
        frame_buffer.set(10, 3, 65)
        frame_buffer.set(10, 4, 66)
        frame_buffer.set(10, 5, 81)

    def do_turn(self):
        key = self.player.move
        if key == "q":
            self.running = False


if __name__ == "__main__":
    from CYLGame import run

    run(TwoDCustomCharSize)
