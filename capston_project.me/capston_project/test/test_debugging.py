import numpy as np
import pytest


def test_integer_overflow_wraps_around_and_wider_type_fixes_it():
    small = np.array([127], dtype=np.int8)
    assert (small + np.int8(1))[0] == -128
    assert (small.astype(np.int64) + 1)[0] == 128


def test_float_to_int_cuts_decimals_instead_of_rounding():
    values = np.array([2.7, 3.9])
    np.testing.assert_array_equal(values.astype(int), [2, 3])
    np.testing.assert_array_equal(np.round(values).astype(int), [3, 4])


def test_nan_spreads_through_sum_but_not_nansum():
    values = np.array([1.0, np.nan, 3.0])
    assert np.isnan(values.sum())
    assert np.nansum(values) == 4.0


def test_broadcasting_needs_compatible_shapes():
    table = np.ones((3, 2))
    with pytest.raises(ValueError):
        table + np.ones(3)
    assert (table + np.ones((3, 1))).shape == (3, 2)


def test_slice_is_a_view_and_mask_is_a_copy():
    original = np.array([1.0, 2.0, 3.0, 4.0])
    view = original[:2]
    view[0] = 99
    assert original[0] == 99

    copy = original[original > 2]
    copy[0] = -1
    assert original[2] == 3


def test_division_by_zero_gives_inf_without_crashing_inside_errstate():
    with np.errstate(divide="ignore"):
        result = np.array([1.0]) / np.array([0.0])
    assert np.isinf(result[0])


def test_vectorized_calculation_matches_plain_loop():
    rng = np.random.default_rng(7)
    quantity = rng.integers(1, 6, 200)
    price = rng.uniform(20, 130, 200)
    rate = rng.choice([0, 0.05, 0.10, 0.20], 200)

    vectorized = quantity * price * (1 - rate)
    looped = np.array([q * p * (1 - r) for q, p, r in zip(quantity, price, rate)])

    np.testing.assert_allclose(vectorized, looped)


def test_isclose_handles_float_rounding():
    assert 0.1 + 0.2 != 0.3
    assert np.isclose(0.1 + 0.2, 0.3)