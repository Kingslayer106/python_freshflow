import numpy as np
import pytest

from freshflow.metrics import build_metrics
from freshflow.stats import describe, group_performance, iqr_fences, ranking, skewness
from tests.test_validation import make_data, make_row


def test_mean_is_pulled_up_by_one_large_value():
    result = describe(np.array([1.0, 2.0, 3.0, 4.0, 100.0]))
    assert result["mean"] == pytest.approx(22.0)
    assert result["median"] == pytest.approx(3.0)
    assert result["skewness"] > 0


def test_describe_ignores_nan_and_reports_count():
    result = describe(np.array([1.0, np.nan, 3.0]))
    assert result["count"] == 2
    assert result["mean"] == pytest.approx(2.0)


def test_symmetric_values_have_zero_skew():
    assert skewness(np.array([1.0, 2.0, 3.0])) == pytest.approx(0.0)


def test_iqr_fences():
    low, high = iqr_fences(np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
    assert low == pytest.approx(-1.0)
    assert high == pytest.approx(7.0)


def group_test_data():
    return make_data(
        make_row(transaction_id=1, outlet_id=1, quantity=2, unit_price=100.0, unit_cost=40.0, discount_rate=0.10),
        make_row(transaction_id=2, outlet_id=1, quantity=3, unit_price=50.0, unit_cost=30.0, discount_rate=0.0),
        make_row(transaction_id=3, outlet_id=2, quantity=4, unit_price=75.5, unit_cost=50.0, discount_rate=0.20),
        make_row(transaction_id=4, outlet_id=2, quantity=1, unit_price=120.0, unit_cost=70.0, discount_rate=0.50),
        make_row(transaction_id=5, outlet_id=3, quantity=5, unit_price=20.0, unit_cost=12.0, discount_rate=0.15),
    )


def test_group_performance_by_outlet_hand_calculated():
    data = group_test_data()
    result = group_performance(data, build_metrics(data), "outlet_id")
    np.testing.assert_array_equal(result["keys"], [1, 2, 3])
    np.testing.assert_allclose(result["units"], [5, 5, 5])
    np.testing.assert_allclose(result["revenue"], [330, 301.6, 85])
    np.testing.assert_allclose(result["profit"], [160, 31.6, 25])
    np.testing.assert_allclose(result["margin_pct"], [48.484848, 10.477454, 29.411765], rtol=1e-6)
    assert result["revenue_share_pct"].sum() == pytest.approx(100.0)


def test_missing_price_counts_units_but_not_revenue():
    data = make_data(
        make_row(transaction_id=1, outlet_id=1, quantity=2, unit_price=100.0, unit_cost=40.0, discount_rate=0.0),
        make_row(transaction_id=2, outlet_id=1, quantity=3, unit_price=np.nan, unit_cost=40.0, discount_rate=0.0),
    )
    result = group_performance(data, build_metrics(data), "outlet_id")
    assert result["units"][0] == 5
    assert result["revenue"][0] == pytest.approx(200.0)


def test_ranking_orders_highest_first():
    data = group_test_data()
    result = group_performance(data, build_metrics(data), "outlet_id")
    np.testing.assert_array_equal(ranking(result, "revenue"), [1, 2, 3])
    np.testing.assert_array_equal(ranking(result, "margin_pct"), [1, 3, 2])