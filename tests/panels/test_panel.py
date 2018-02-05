import pytest

from CYLGame import Panel, PanelBorder
from CYLGame.Frame import GridFrameBuffer


def test_edges():
    panel = Panel(1, 1, 1, 1, border=PanelBorder.create("2", "7", "5", "4", "3", "1", "8", "6"))
    frame = GridFrameBuffer(5, 5, init_value=" ")
    panel.redraw(frame)
    exp = ["123  ",
           "4 5  ",
           "678  ",
           "     ",
           "     "]
    exp_frame = GridFrameBuffer.from_string_array(exp)
    assert frame == exp_frame


def test_edges_2():
    panel = Panel(0, 0, 1, 1, border=PanelBorder.create("2", "7", "5", "4", "3", "1", "8", "6"))
    frame = GridFrameBuffer(5, 5, init_value=" ")
    with pytest.raises(IndexError):
        panel.redraw(frame)
