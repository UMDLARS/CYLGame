from pathlib import Path
from CYLGame.Frame import GridFrameBuffer
from CYLGame.Game import ConstMapping, GridGame
from CYLGame.Player import DefaultGridPlayer
from CYLGame.Sprite import SpriteSet


class CustomCharSize(GridGame):
    SCREEN_WIDTH = 8
    SCREEN_HEIGHT = 4
    CHAR_WIDTH = 56
    CHAR_HEIGHT = 88
    CHAR_SET = "resources/terminal7x11_gs_ro.png"

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
    
    def do_turn(self):
        key = self.player.move
        if key == 'q':
            self.running = False



if __name__ == "__main__":
    from CYLGame import run

    run(CustomCharSize)
