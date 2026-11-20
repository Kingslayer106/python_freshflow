import numpy as np
import pytest

from freshflow.metrics import build_metrics, summarize
from tests.test_validation import make_data, make_row

FIVE_ROWS = make_data(
    make_row(transaction_id=1, quantity=2, unit_price=100.0, unit_cost=40.0, discount_rate=0.10),
    make_row(transaction_id=2, quantity=3, unit_price=50.0, unit_cost=30.0, discount_rate=0.0),
    make_row(transaction_id=3, quantity=4, unit_price=75.5, unit_cost=50.0, discount_rate=0.20),
    make_row(transaction_id=4, quantity=1, unit_price=120.0, unit_cost=70.0, discount_rate=0.50),
    make_row(transaction_id=5, quantity=5, unit_price=20.0, unit_cost=12.0, discount_rate=0.15),
)


def test_five_hand_calculated_rows():
    metrics = build_metrics(FIVE_ROWS)
    np.testing.assert_allclose(metrics["gross_sales"], [200, 150, 302, 120, 100])
    np.testing.assert_allclose(metrics["discount_amount"], [20, 0, 60.4, 60, 15])
    np.testing.assert_allclose(metrics["net_revenue"], [180, 150, 241.6, 60, 85])
    np.testing.assert_allclose(metrics["cogs"], [80, 90, 200, 70, 60])
    np.testing.assert_allclose(metrics["gross_profit"], [100, 60, 41.6, -10, 25])
    np.testing.assert_allclose(metrics["margin_pct"], [55.555556, 40, 17.218543, -16.666667, 29.411765], rtol=1e-6)
    np.testing.assert_allclose(metrics["avg_selling_price"], [90, 50, 60.4, 60, 17])


def test_missing_price_gives_nan_revenue_and_profit():
    metrics = build_metrics(make_data(make_row(unit_price=np.nan)))
    assert np.isnan(metrics["net_revenue"][0])
    assert np.isnan(metrics["gross_profit"][0])


def test_missing_cost_keeps_revenue_but_not_profit():
    metrics = build_metrics(make_data(make_row(unit_cost=np.nan)))
    assert not np.isnan(metrics["net_revenue"][0])
    assert np.isnan(metrics["gross_profit"][0])


def test_zero_revenue_margin_is_nan():
    metrics = build_metrics(make_data(make_row(discount_rate=1.0)))
    assert metrics["net_revenue"][0] == 0
    assert np.isnan(metrics["margin_pct"][0])


def test_average_selling_price_needs_positive_quantity():
    metrics = build_metrics(make_data(make_row(quantity=0)))
    assert np.isnan(metrics["avg_selling_price"][0])


def test_overall_margin_is_not_the_average_of_row_margins():
    summary = summarize(FIVE_ROWS, build_metrics(FIVE_ROWS))
    row_margin_average = np.mean(build_metrics(FIVE_ROWS)["margin_pct"])
    assert summary["gross margin %"] == pytest.approx(216.6 / 716.6 * 100)
    assert summary["gross margin %"] != pytest.approx(row_margin_average)


def test_margin_uses_same_rows_as_profit():
    data = np.vstack((FIVE_ROWS, make_row(transaction_id=6, quantity=2, unit_price=100.0, unit_cost=np.nan, discount_rate=0.0)))
    summary = summarize(data, build_metrics(data))
    assert summary["rows with revenue"] == 6
    assert summary["rows with profit"] == 5
    assert summary["net revenue"] == pytest.approx(916.6)
    assert summary["gross margin %"] == pytest.approx(216.6 / 716.6 * 100)


def test_one_dimensional_input_raises_error():
    with pytest.raises(IndexError):
        build_metrics(np.array([1.0, 2.0, 3.0]))