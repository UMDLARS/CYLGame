from dataclasses import dataclass

import pygame

from CYLGame.Sprite import SpriteSet

PYGAME_SCREEN = None


def get_clock():
    return pygame.time.Clock()


class Display:
    def __init__(self, width, height, title=None):
        self.width = width
        self.height = height
        self.title = title

    def get_size(self):
        return self.width, self.height

    def get_keys(self):
        """Gets the keys that were press since last time you called this function.

        Returns:
            Key
        """
        raise NotImplementedError("This is an abstract method.")

    def update(self, frame_buffer):
        """Updates the display with the buffer given.

        Args:
            frame_buffer(FrameBuffer): The buffer to use when redrawing the screen.
        """
        raise NotImplementedError("This is an abstract method.")


class PyGameDisplay(Display):
    def __init__(self, width, height, title=None):
        super(PyGameDisplay, self).__init__(width, height, title)
        global PYGAME_SCREEN
        if not PYGAME_SCREEN:
            # Init pygame
            global pygame
            import pygame

            pygame.init()
            PYGAME_SCREEN = pygame.display.set_mode((self.width, self.height))
            if self.title:
                pygame.display.set_caption(self.title)
        else:
            raise Exception("You are trying the run two games at the time! I can't do that :(")

    def get_keys(self):
        keys = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit()
            elif event.type == pygame.KEYDOWN and 0 < event.key < 256:
                char = chr(event.key)
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    # Shift was being pressed.
                    char = char.upper()
                keys += [char]
        return keys

    def update(self, frame_buffer):
        frame_buffer.draw_to_surface(PYGAME_SCREEN)
        pygame.display.flip()


@dataclass
class CharSet(SpriteSet):
    def __post_init__(self):
        self.img = pygame.image.load(self.image_filepath)
        self.cache = {}

    @classmethod
    def from_sprite_set(cls, sprite_set):
        return cls(
            image_filepath=sprite_set.image_filepath,
            char_width=sprite_set.char_width,
            char_height=sprite_set.char_height,
            char_rows=sprite_set.char_rows,
            char_columns=sprite_set.char_columns,
        )

    def create_char_img(self, char):
        row = char % self.char_columns
        col = char // self.char_columns

        crop_dim = (
            row * self.char_width,
            col * self.char_height,
            (row + 1) * self.char_width,
            (col + 1) * self.char_height,
        )
        img = pygame.Surface((self.char_width, self.char_height), flags=pygame.SRCALPHA)
        img.blit(self.img, (0, 0), crop_dim)

        return img

    def get_img(self, char):
        if char not in self.cache:
            self.cache[char] = self.create_char_img(char)
        return self.cache[char]

    def pix_size_to_char(self, size):
        return size[0] // self.char_width, size[1] // self.char_height

    def char_size_to_pix(self, size):
        return size[0] * self.char_width, size[1] * self.char_height
