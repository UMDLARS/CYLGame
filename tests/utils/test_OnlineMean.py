import pytest

from CYLGame.Utils import OnlineMean

LISTS_OF_NUMBERS = (
    [0],
    [0, 1],
    [0, 1, 2],
    [0, 0, 0],
    [0, 0, 0, 1],
    [-1, 1],
    [1.5, 2.5],
)


NUMBERS_TO_MEAN = [(nums, sum(nums) / len(nums)) for nums in LISTS_OF_NUMBERS]


@pytest.mark.parametrize("inp,out", NUMBERS_TO_MEAN)
def test_add(inp, out):
    online_mean = OnlineMean()
    for i in inp:
        online_mean.add(i)
    assert online_mean.mean == out


@pytest.mark.parametrize("inp,out", NUMBERS_TO_MEAN)
def test_add_op(inp, out):
    online_mean = OnlineMean()
    for i in inp:
        online_mean = online_mean + i
    assert online_mean.mean == out


@pytest.mark.parametrize(
    "inp,out",
    (
        ([0, 1], 0),
        ([1.15, 1.33], 1),
        ([1.75, 1.80], 1),
    ),
)
def test_floored_mean(inp, out):
    online_mean = OnlineMean()
    for i in inp:
        online_mean.add(i)
    assert online_mean.floored_mean == out


@pytest.mark.parametrize(
    "nums,places,out",
    (
        ([0, 1], 0, 0),
        ([0, 1], 2, 0.5),
        ([1, 1], 0, 1),
        ([1, 1], 2, 1),
        ([1, 1, 2], 0, 1),
        ([1, 1, 2], 2, 1.33),
        ([1, 2, 2], 0, 2),
        ([1, 2, 2], 2, 1.67),
    ),
)
def test_rounded_mean(nums, places, out):
    online_mean = OnlineMean()
    for n in nums:
        online_mean.add(n)
    assert online_mean.rounded_mean(places=places) == out


@pytest.mark.parametrize(
    "nums,rolling_n,out",
    (
        ([0, 100, 100, 100, 100, 100], 2, 96.88),
        ([0] + [100] * 10, 10, 91),
    ),
)
def test_rolling_n(nums, rolling_n, out):
    online_mean = OnlineMean(roll_after_n=rolling_n)
    for n in nums:
        online_mean.add(n)
    assert online_mean.rounded_mean(2) == round(out, 2)
