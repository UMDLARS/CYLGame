from typing import Union

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SpriteSet:
    image_filepath: Path
    char_width: int
    char_height: int
    char_rows: int
    char_columns: int

    def is_char_valid(self, char: Union[str, int]):
        if isinstance(char, str):
            char = ord(char)
        return 0 <= char < self.char_rows * self.char_columns
