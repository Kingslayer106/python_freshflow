import numpy as np
import pytest

from freshflow.metrics import build_metrics
from freshflow.trends import daily_change, daily_pct_change, daily_totals, rolling_average, unusual_changes
from tests.test_validation import make_data, make_row


def test_daily_totals_hand_calculated():
    data = make_data(
        make_row(transaction_id=1, day_index=1, quantity=2, unit_price=100.0, discount_rate=0.0),
        make_row(transaction_id=2, day_index=1, quantity=1, unit_price=50.0, discount_rate=0.0),
        make_row(transaction_id=3, day_index=3, quantity=1, unit_price=80.0, discount_rate=0.5),
    )
    revenue, transactions = daily_totals(data, build_metrics(data))
    assert len(revenue) == 30
    assert revenue[0] == pytest.approx(250.0)
    assert revenue[1] == 0
    assert revenue[2] == pytest.approx(40.0)
    np.testing.assert_array_equal(transactions[:3], [2, 0, 1])


def test_missing_price_row_is_not_counted_as_revenue_day():
    data = make_data(make_row(day_index=5, unit_price=np.nan))
    revenue, transactions = daily_totals(data, build_metrics(data))
    assert revenue[4] == 0
    assert transactions[4] == 0


def test_daily_change_and_pct_change():
    revenue = np.array([100.0, 150.0, 75.0])
    np.testing.assert_allclose(daily_change(revenue), [50, -75])
    np.testing.assert_allclose(daily_pct_change(revenue), [50, -50])


def test_pct_change_is_nan_when_previous_day_is_zero():
    result = daily_pct_change(np.array([0.0, 10.0]))
    assert np.isnan(result[0])


def test_rolling_average():
    result = rolling_average(np.array([1.0, 2.0, 3.0, 4.0, 5.0]), window=3)
    np.testing.assert_allclose(result, [np.nan, np.nan, 2, 3, 4])


def test_unusual_change_is_flagged():
    revenue = np.array([100.0, 101.0, 99.0, 100.0, 102.0, 98.0, 100.0, 101.0, 99.0, 100.0,
                        300.0, 100.0, 101.0, 99.0, 100.0, 102.0, 98.0, 100.0, 101.0, 99.0])
    _, flagged = unusual_changes(revenue)
    assert flagged[9]
    assert flagged[10]
    assert flagged.sum() == 2


def test_constant_revenue_has_no_unusual_change():
    _, flagged = unusual_changes(np.array([10.0, 10.0, 10.0]))
    assert not flagged.any()