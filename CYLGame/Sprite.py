from typing import Any, Dict, List, Optional, Tuple, Union

import itertools
from dataclasses import InitVar, dataclass
from functools import reduce
from pathlib import Path

from .Utils import prefix_filename


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


@dataclass
class MultiDimensionalSpriteColoring:
    """
    This is a class for coloring sprites with multiple dimensions.
    """

    base_sprite_set: InitVar[SpriteSet]
    mappings: List[Dict[Any, Tuple[Tuple[int, int, int], Tuple[int, int, int]]]]
    sprite_set: Optional[SpriteSet] = None  # generated on init based on above values

    def __post_init__(self, base_sprite_set):
        from PIL import Image

        self._orig_size = base_sprite_set.char_rows * base_sprite_set.char_columns

        self.sprite_set = base_sprite_set
        img = Image.open(base_sprite_set.image_filepath).convert(mode="RGB")

        assert (
            img.width == base_sprite_set.char_width * base_sprite_set.char_rows
        ), "Image width doesn't match sprite char width and rows"
        assert (
            img.height == base_sprite_set.char_height * base_sprite_set.char_columns
        ), "Image height doesn't match sprite char height and columns"

        height_increase_factor = reduce(lambda a, b: a * b, (len(x) + 1 for x in self.mappings))
        full_img = Image.new(mode="RGB", size=(img.width, img.height * height_increase_factor))

        print(height_increase_factor)

        index_key_colors = [
            [
                (i, key, old_color, new_color)
                for i, (key, (old_color, new_color)) in enumerate(
                    itertools.chain([(None, (None, None))], mapping.items())
                )
            ]
            for mapping in self.mappings
        ]
        print(index_key_colors)
        mapping_index_to_inner_size = [1]
        for x in reversed(self.mappings):
            mapping_len = len(x) + 1
            mapping_index_to_inner_size.insert(0, mapping_index_to_inner_size[0] * mapping_len)
        mapping_index_to_inner_size.pop(0)
        print(mapping_index_to_inner_size)

        self._mapping_keys_to_index = {}
        for x, mapping in enumerate(index_key_colors):
            base_size = mapping_index_to_inner_size[x]
            self._mapping_keys_to_index[x] = {}
            for index, key, _, _ in mapping:
                if key is not None:
                    self._mapping_keys_to_index[x][key] = base_size * index

        print(self._mapping_keys_to_index)

        for ful_img_index, pairs in enumerate(itertools.product(*index_key_colors)):
            new_img = img.copy()
            for mapping_index, (index, key, old_color, new_color) in enumerate(pairs):
                if old_color is not None:
                    self._replace(new_img, old_color, new_color)
            full_img.paste(new_img, (0, ful_img_index * img.height))
        new_path = prefix_filename(base_sprite_set.image_filepath, prefix="generated_")
        full_img.save(new_path)
        print(base_sprite_set)
        self.sprite_set = SpriteSet(
            image_filepath=new_path,
            char_width=base_sprite_set.char_width,
            char_height=base_sprite_set.char_height,
            char_rows=base_sprite_set.char_rows * height_increase_factor,
            char_columns=base_sprite_set.char_columns,
        )
        print(self.sprite_set)

    @staticmethod
    def _replace(img, old_color, new_color):
        """Replace one color for another in a given image."""
        img_data = img.load()
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                if img_data[x, y] == old_color:
                    img_data[x, y] = new_color

    def get_mapping_value(self, index: int, key: Any):
        assert self._mapping_keys_to_index is not None
        return self._mapping_keys_to_index[index][key] * self._orig_size


@dataclass
class TwoDimensionalSpriteColoring:
    """
    This is a class for coloring a sprite with foreground and background colors.
    """

    base_sprite_set: InitVar[SpriteSet]
    foreground_mapping: Dict[Any, Tuple[int, int, int]]
    background_mapping: Dict[Any, Tuple[int, int, int]]
    base_foreground_color: Tuple[int, int, int] = (255, 255, 255)
    base_background_color: Tuple[int, int, int] = (0, 0, 0)
    sprite_set: Optional[SpriteSet] = None  # generated on init based on above values
    _coloring: Optional[MultiDimensionalSpriteColoring] = None

    def __post_init__(self, base_sprite_set):
        mappings = [
            {k: (self.base_foreground_color, v) for k, v in self.foreground_mapping.items()},
            {k: (self.base_background_color, v) for k, v in self.background_mapping.items()},
        ]
        self._coloring = MultiDimensionalSpriteColoring(base_sprite_set=base_sprite_set, mappings=mappings)
        self.sprite_set = self._coloring.sprite_set

    def get_foreground_value(self, key: Any):
        assert self._coloring is not None
        return self._coloring.get_mapping_value(0, key=key)

    def get_background_value(self, key: Any):
        assert self._coloring is not None
        return self._coloring.get_mapping_value(1, key=key)


@dataclass
class Char:
    value: int

    @classmethod
    def from_str(cls, c):
        return cls(ord(c))

    def __str__(self):
        return chr(self.value)

    def __add__(self, other):
        if isinstance(other, str):
            other = Char.from_str(other)
        if isinstance(other, int):
            other = Char(other)
        if isinstance(other, Char):
            return Char(self.value + other.value)

    def __radd__(self, other):
        return self + other

    def __eq__(self, other):
        if isinstance(other, Char):
            return self.value == other.value
        elif isinstance(other, str):
            return str(self) == other
        elif isinstance(other, int):
            return self.value == other
        raise TypeError(f"Can not compare types `{type(self)}` and `{type(other)}`")
