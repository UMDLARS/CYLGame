import filecmp

from CYLGame.Sprite import MultiDimensionalSpriteColoring, SpriteSet


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
