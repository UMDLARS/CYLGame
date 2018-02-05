from CYLGame import MapPanel
from CYLGame.Frame import GridFrameBuffer


def test_edges():
    panel = MapPanel(1, 1, 2, 2)
    frame = GridFrameBuffer(5, 5, init_value=" ")
    panel.add("1", (0, 0))
    panel.add("2", (1, 0))
    panel.add("3", (0, 1))
    panel.add("4", (1, 1))
    panel.redraw(frame)
    exp = ["     ",
           " 12  ",
           " 34  ",
           "     ",
           "     "]
    exp_frame = GridFrameBuffer.from_string_array(exp)
    assert frame == exp_frame
