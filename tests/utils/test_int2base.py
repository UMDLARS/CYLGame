import pytest

from CYLGame.Utils import int2base


@pytest.mark.parametrize('i,base,out', (
        (0, 2, "0"),
        (1, 2, "1"),
        (-1, 2, "-1"),
        (1, 32, "1"),
        (123_789_213, 16, "760df9d"),
        (123_789_213, 32, "3m1nst"),
        (123_789_213, 36, "21p8d9"),
        (-123_789_213, 36, "-21p8d9"),
))
def test_int2base(i, base, out):
    assert int2base(i, base) == out


@pytest.mark.parametrize('i,base', (
        (12, 1),
        (123321, 1),
        (0, 1),
        (123213213, 128),
        (123213, 37)
))
def test_choose_not_implemented_cases(i, base):
    with pytest.raises(ValueError):
        int2base(i, base)
