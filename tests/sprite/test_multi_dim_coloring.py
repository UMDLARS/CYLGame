import filecmp

import pytest

from CYLGame.Sprite import Char, MultiDimensionalSpriteColoring, SpriteSet


def test_basic_smoke(resource_path_root):
    input_image_path = resource_path_root / "terminal16x16_gs_ro.png"
    coloring = MultiDimensionalSpriteColoring(
        base_sprite_set=SpriteSet(
            char_width=16,
            char_height=16,
            char_rows=16,
            char_columns=16,
            image_filepath=input_image_path,
        ),
        mappings=[
            {"green": ((255, 255, 255), (0, 255, 0))},
            {"water": ((0, 0, 0), (0, 0, 255)), "dirt": ((0, 0, 0), (150, 75, 0))},
        ],
    )
    assert filecmp.cmp(
        resource_path_root / "expected_basic_smoke_test_result_terminal16x16_gs_ro.png",
        coloring.sprite_set.image_filepath,
    )


def test_operations_on_chars(resource_path_root):
    input_image_path = resource_path_root / "terminal16x16_gs_ro.png"
    coloring = MultiDimensionalSpriteColoring(
        base_sprite_set=SpriteSet(
            char_width=16,
            char_height=16,
            char_rows=16,
            char_columns=16,
            image_filepath=input_image_path,
        ),
        mappings=[
            {"green": ((255, 255, 255), (0, 255, 0))},
            {"water": ((0, 0, 0), (0, 0, 255)), "dirt": ((0, 0, 0), (150, 75, 0))},
        ],
    )
    GREEN = coloring.get_mapping_value(0, "green")
    WATER = coloring.get_mapping_value(1, "water")
    DIRT = coloring.get_mapping_value(1, "dirt")

    excepted_green_a_value = 865
    assert 97 + GREEN == excepted_green_a_value
    assert "a" + GREEN == excepted_green_a_value
    assert Char(97) + GREEN == excepted_green_a_value
    assert Char.from_str("a") + GREEN == excepted_green_a_value
    assert GREEN + 97 == excepted_green_a_value
    assert GREEN + "a" == excepted_green_a_value
    assert GREEN + Char(97) == excepted_green_a_value
    assert GREEN + Char.from_str("a") == excepted_green_a_value

    excepted_green_dirt_a_value = 1377
    assert GREEN + DIRT + 97 == excepted_green_dirt_a_value
    assert GREEN + DIRT + "a" == excepted_green_dirt_a_value
    assert GREEN + DIRT + Char(97) == excepted_green_dirt_a_value
    assert GREEN + 97 + DIRT == excepted_green_dirt_a_value
    assert GREEN + "a" + DIRT == excepted_green_dirt_a_value
    assert GREEN + Char(97) + DIRT == excepted_green_dirt_a_value
    assert 97 + GREEN + DIRT == excepted_green_dirt_a_value
    assert "a" + GREEN + DIRT == excepted_green_dirt_a_value
    assert Char(97) + GREEN + DIRT == excepted_green_dirt_a_value

    assert (Char(97) + GREEN).modifiers == (GREEN,)
    assert (Char(97) + GREEN + DIRT).modifiers == (GREEN, DIRT)

    with pytest.raises(ValueError):
        WATER + DIRT

    with pytest.raises(ValueError):
        DIRT + 97 + WATER

    with pytest.raises(ValueError):
        DIRT + "a" + WATER

    with pytest.raises(ValueError):
        DIRT + WATER + "a"

    with pytest.raises(ValueError):
        "a" + DIRT + WATER

    with pytest.raises(TypeError):
        "a" + Char(1)

    with pytest.raises(TypeError):
        23 + Char(1)

    with pytest.raises(TypeError):
        Char(1) + Char(23)

    with pytest.raises(TypeError):
        Char(1) + DIRT + "a"

    with pytest.raises(TypeError):
        Char(1) + DIRT + Char(23)
