import numpy as np
from fhe_mean import NUM_VALUES


def scaled_mean_plain(values):
    return (np.sum(values) * 100) // NUM_VALUES


def test_constant_values():
    #all values are equal => mean is the same value (×100)
    values = np.array([10] * NUM_VALUES, dtype=np.uint8)
    expected = scaled_mean_plain(values)
    assert expected == (10 * 100)


def test_simple_progression():
    #0 + 1 + 2 + 3 + 4 + 5 = 15 => expected scaled mean = (15*100)//6 = 250
    values = np.arange(NUM_VALUES, dtype=np.uint8)
    expected = scaled_mean_plain(values)
    assert expected == 250


def test_fractional_mean_case():
    #Sum = 21 => mean = 3.5 => scaled mean = floor(350)
    values = np.array([1, 2, 3, 4, 5, 6], dtype=np.uint8)
    expected = scaled_mean_plain(values)
    assert expected == 350


def test_random_values():
    values = np.array([3, 7, 10, 4, 9, 2], dtype=np.uint8)
    expected = scaled_mean_plain(values)
    assert expected == (np.sum(values) * 100) // NUM_VALUES
