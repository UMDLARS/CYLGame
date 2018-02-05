from CYLGame.Frame import GridFrameBuffer


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
