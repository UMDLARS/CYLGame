from pathlib import Path

from CYLGame.Frame import GridFrameBuffer
from CYLGame.Game import ConstMapping, GridGame
from CYLGame.Player import DefaultGridPlayer
from CYLGame.Sprite import SpriteSet


class CustomCharSize(GridGame):
    SCREEN_WIDTH = 16
    SCREEN_HEIGHT = 8
    CHAR_WIDTH = 56
    CHAR_HEIGHT = 88
    CHAR_SET = "resources/terminal56x88_gs_ro.png"

    @staticmethod
    def get_intro():
        return "Test"

    @staticmethod
    def default_prog_for_bot(_):
        return ""

    @classmethod
    def get_sprite_set(cls) -> SpriteSet:
        return SpriteSet(
            char_width=cls.CHAR_WIDTH,
            char_height=cls.CHAR_HEIGHT,
            char_rows=2,
            char_columns=3,
            image_filepath=Path(cls.CHAR_SET),
        )

    def __init__(self, random):
        super().__init__(random)
        self.running = True
        self.turns = 0

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
        # Remove trail
        frame_buffer.set(1 + self.turns, 1, 0)
        frame_buffer.set(1 + self.turns, 2, 0)

        # Draw new image
        frame_buffer.set(2 + self.turns, 1, 0)
        frame_buffer.set(3 + self.turns, 1, 1)
        frame_buffer.set(4 + self.turns, 1, 2)
        frame_buffer.set(2 + self.turns, 2, 3)
        frame_buffer.set(3 + self.turns, 2, 4)
        frame_buffer.set(4 + self.turns, 2, 5)

    def do_turn(self):
        key = self.player.move
        self.turns += 1
        if key == "q" or self.turns > 5:
            self.running = False

    def get_score(self):
        return 0


if __name__ == "__main__":
    from CYLGame import run

    run(CustomCharSize)
