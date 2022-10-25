from CYLGame import MapPanel
from CYLGame.Frame import GridFrameBuffer
from CYLGame.Sprite import Char


def test_edges():
    panel = MapPanel(1, 1, 2, 2)
    frame = GridFrameBuffer(5, 5, init_value=" ")
    panel.add("1", (0, 0))
    panel.add("2", (1, 0))
    panel.add("3", (0, 1))
    panel.add("4", (1, 1))
    panel.redraw(frame)
    exp = ["     ", " 12  ", " 34  ", "     ", "     "]
    exp_frame = GridFrameBuffer.from_string_array(exp)
    assert frame == exp_frame


def test_different_types():
    panel = MapPanel(0, 0, 1, 3)
    frame = GridFrameBuffer(1, 3)
    panel.add("a", (0, 0))
    panel.add(97, (0, 1))
    panel.add(Char(97), (0, 2))
    panel.redraw(frame)
    assert frame == GridFrameBuffer.from_string_array("aaa")
