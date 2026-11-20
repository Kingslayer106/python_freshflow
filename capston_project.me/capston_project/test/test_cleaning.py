import numpy as np

from freshflow.cleaning import clean_data
from freshflow.loader import COL
from tests.test_validation import make_data, make_row


def test_raw_data_is_not_changed():
    data = make_data(make_row(quantity=-1), make_row(transaction_id=2, customer_rating=9))
    before = data.copy()
    clean_data(data)
    np.testing.assert_array_equal(data, before)


def test_invalid_row_is_excluded_and_kept_in_excluded_array():
    data = make_data(make_row(), make_row(transaction_id=2, discount_rate=2.0))
    clean, excluded, _, _ = clean_data(data)
    assert len(clean) == 1
    assert len(excluded) == 1
    assert excluded.shape[1] == 13


def test_invalid_rating_becomes_nan_and_row_is_kept():
    data = make_data(make_row(customer_rating=9))
    clean, _, _, _ = clean_data(data)
    assert len(clean) == 1
    assert np.isnan(clean[0, COL["customer_rating"]])


def test_missing_price_and_rating_rows_are_kept():
    data = make_data(make_row(unit_price=np.nan, customer_rating=np.nan))
    clean, _, _, _ = clean_data(data)
    assert len(clean) == 1


def test_id_collision_with_different_fields_is_kept():
    data = make_data(make_row(transaction_id=1), make_row(transaction_id=1, day_index=9))
    clean, _, _, _ = clean_data(data)
    assert len(clean) == 2


def test_exact_copy_keeps_only_first():
    data = make_data(make_row(transaction_id=1), make_row(transaction_id=1))
    clean, _, _, _ = clean_data(data)
    assert len(clean) == 1