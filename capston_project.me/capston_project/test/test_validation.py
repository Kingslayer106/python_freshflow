import numpy as np

from freshflow.loader import COL
from freshflow.validation import invalid_masks, missing_masks, rule_counts

BASE_ROW = [1, 5, 1, 1, 1, 2, 100.0, 40.0, 0.1, 20, 1, 4.0]


def make_row(**changes):
    row = BASE_ROW.copy()
    for name, value in changes.items():
        row[COL[name]] = value
    return row


def make_data(*rows):
    return np.array(rows, dtype=float)


def test_clean_row_has_no_violations():
    masks = invalid_masks(make_data(make_row()))
    assert not any(mask.any() for mask in masks.values())


def test_duplicate_ids_are_flagged():
    data = make_data(make_row(transaction_id=1), make_row(transaction_id=1), make_row(transaction_id=2))
    mask = invalid_masks(data)["duplicate transaction_id"]
    np.testing.assert_array_equal(mask, [True, True, False])


def test_category_mismatch():
    data = make_data(make_row(), make_row(transaction_id=2, product_code=7, category_code=4))
    mask = invalid_masks(data)["category mismatch"]
    np.testing.assert_array_equal(mask, [False, True])


def test_nan_price_is_missing_not_invalid():
    data = make_data(make_row(unit_price=np.nan))
    assert not invalid_masks(data)["price not positive"].any()
    assert missing_masks(data)["missing unit_price"].all()


def test_missing_rating_is_not_invalid():
    data = make_data(make_row(customer_rating=np.nan), make_row(transaction_id=2, customer_rating=9))
    np.testing.assert_array_equal(invalid_masks(data)["invalid rating"], [False, True])


def test_bad_quantity_and_discount():
    data = make_data(make_row(quantity=0), make_row(transaction_id=2, discount_rate=1.5))
    masks = invalid_masks(data)
    np.testing.assert_array_equal(masks["quantity not positive"], [True, False])
    np.testing.assert_array_equal(masks["discount outside 0-1"], [False, True])


def test_unique_rows_vs_total_violations():
    data = make_data(make_row(quantity=-1, discount_rate=2.0), make_row(transaction_id=2))
    result = rule_counts(invalid_masks(data))
    assert result["total_violations"] == 2
    assert result["unique_rows_affected"] == 1