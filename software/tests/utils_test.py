import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest

import utils

def test_clamp_low():
    assert utils.clamp(-1, 0, 2) == 0

def test_clamp_high():
    assert utils.clamp(4, 0, 2) == 2

def test_clamp_mid():
    assert utils.clamp(1, 0, 2) == 1

interpolate_test_data = [
    # Normal output ranges
    (0, 1, 10, 0, 100, 10),
    (0, 5, 10, 0, 100, 50),
    (0, 9, 10, 0, 100, 90),

    # Backward output ranges
    (0, 5, 10, 100, 0, 50),
    (0, 1, 10, 100, 0, 90),
    (0, 9, 10, 100, 0, 10),

    # Input outside input range
    (0, 15, 10, 0, 100, 150),

    # Backward input ranges
    (10, 1, 0, 0, 100, 90),
    (10, 9, 0, 0, 100, 10),
]
@pytest.mark.parametrize("in_min, value_in, in_max, out_min, out_max, expected", interpolate_test_data)
def test_interpolate(in_min, value_in, in_max, out_min, out_max, expected):
    assert utils.interpolate(in_min, value_in, in_max, out_min, out_max) == expected
    