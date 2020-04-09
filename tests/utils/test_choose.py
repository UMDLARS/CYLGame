import pytest

from CYLGame.Utils import choose


@pytest.mark.parametrize('n,k,out', (
        (1, 1, 1),
        (2, 2, 1),
        (52, 5, 2_598_960),
        (4, 2, 6),
))
def test_choose(n, k, out):
    assert choose(n, k) == out
