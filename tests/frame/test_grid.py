import pytest

from CYLGame.Frame import GridFrameBuffer
from CYLGame.Sprite import SpriteSet


def test_str_1x1():
    frame = GridFrameBuffer(1, 1)
    frame.set(0, 0, "a")
    assert str(frame) == "a"


def test_str_2x2():
    frame = GridFrameBuffer(2, 2)
    frame.set(0, 0, "a")
    frame.set(1, 0, "b")
    frame.set(0, 1, "c")
    frame.set(1, 1, "d")
    assert str(frame) == "ab\ncd"


def test_eq_1x1():
    frame1 = GridFrameBuffer(1, 1)
    frame1.set(0, 0, "a")
    frame2 = GridFrameBuffer(1, 1)
    frame2.set(0, 0, "a")
    assert frame1 == frame2


def test_neq_1x1():
    frame1 = GridFrameBuffer(1, 1)
    frame1.set(0, 0, "a")
    frame2 = GridFrameBuffer(1, 1)
    frame2.set(0, 0, "b")
    assert frame1 != frame2


def test_eq_2x2():
    frame1 = GridFrameBuffer(2, 2)
    frame1.set(0, 0, "a")
    frame1.set(1, 0, "b")
    frame1.set(0, 1, "c")
    frame1.set(1, 1, "d")
    frame2 = GridFrameBuffer(2, 2)
    frame2.set(0, 0, "a")
    frame2.set(1, 0, "b")
    frame2.set(0, 1, "c")
    frame2.set(1, 1, "d")
    assert frame1 == frame2


def test_neq_2x2():
    frame1 = GridFrameBuffer(2, 2)
    frame1.set(0, 0, "a")
    frame1.set(1, 0, "b")
    frame1.set(0, 1, "c")
    frame1.set(1, 1, "d")
    frame2 = GridFrameBuffer(2, 2)
    frame2.set(0, 0, "d")
    frame2.set(1, 0, "b")
    frame2.set(0, 1, "c")
    frame2.set(1, 1, "d")
    assert frame1 != frame2


def test_from_string_array():
    frame1 = GridFrameBuffer(2, 2)
    frame1.set(0, 0, "a")
    frame1.set(1, 0, "b")
    frame1.set(0, 1, "c")
    frame1.set(1, 1, "d")
    frame2 = GridFrameBuffer.from_string_array(["ab", "cd"])
    assert frame1 == frame2


@pytest.mark.parametrize(
    "width, height, x, y, char",
    [
        (1, 1, -1, 0, "a"),
        (1, 1, 0, -1, "a"),
        (1, 1, -100, -100, "a"),
        (1, 1, 2, 0, "a"),
        (1, 1, 100, 100, "a"),
    ],
)
def test_out_of_bounds(width, height, x, y, char):
    frame = GridFrameBuffer(width=width, height=height)
    with pytest.raises(IndexError):
        frame.set(x, y, char=char)


@pytest.mark.parametrize(
    "sprite_set, char",
    [
        (SpriteSet(image_filepath=None, char_width=None, char_height=None, char_rows=1, char_columns=1), 0),
        (SpriteSet(image_filepath=None, char_width=None, char_height=None, char_rows=10, char_columns=10), 99),
        (SpriteSet(image_filepath=None, char_width=None, char_height=None, char_rows=10, char_columns=10), 50),
        (SpriteSet(image_filepath=None, char_width=None, char_height=None, char_rows=10, char_columns=10), 10),
        (SpriteSet(image_filepath=None, char_width=None, char_height=None, char_rows=10, char_columns=10), 9),
        (SpriteSet(image_filepath=None, char_width=None, char_height=None, char_rows=10, char_columns=10), 0),
    ],
)
def test_valid_char(sprite_set, char):
    frame = GridFrameBuffer(width=1, height=1, charset=sprite_set)
    frame.set(0, 0, char)


@pytest.mark.parametrize(
    "sprite_set, char",
    [
        (SpriteSet(image_filepath=None, char_width=None, char_height=None, char_rows=1, char_columns=1), 10),
        (SpriteSet(image_filepath=None, char_width=None, char_height=None, char_rows=1, char_columns=1), 1),
        (SpriteSet(image_filepath=None, char_width=None, char_height=None, char_rows=1, char_columns=1), -1),
        (SpriteSet(image_filepath=None, char_width=None, char_height=None, char_rows=10, char_columns=10), -1),
        (SpriteSet(image_filepath=None, char_width=None, char_height=None, char_rows=10, char_columns=10), -100),
        (SpriteSet(image_filepath=None, char_width=None, char_height=None, char_rows=10, char_columns=10), 100),
        (SpriteSet(image_filepath=None, char_width=None, char_height=None, char_rows=10, char_columns=10), 321),
    ],
)
def test_invalid_char(sprite_set, char):
    frame = GridFrameBuffer(width=1, height=1, charset=sprite_set)
    with pytest.raises(ValueError):
        frame.set(0, 0, char)
