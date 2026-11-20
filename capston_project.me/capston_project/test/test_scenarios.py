import numpy as np
import pytest

from freshflow.metrics import build_metrics
from freshflow.scenarios import (
    BAND_LABELS, baseline_totals, breakeven_quantity_change, discount_bands,
    discount_relationships, percent_change, run_scenario, scenario_table,
)
from tests.test_validation import make_data, make_row

TOTALS = {"rows": 10, "gross": 1000.0, "cogs": 600.0, "discount": 100.0}


def test_band_edges_put_boundary_values_in_the_lower_band():
    data = make_data(
        make_row(transaction_id=1, discount_rate=0.0),
        make_row(transaction_id=2, discount_rate=0.05),
        make_row(transaction_id=3, discount_rate=0.20),
        make_row(transaction_id=4, discount_rate=0.21),
    )
    result = discount_bands(data, build_metrics(data))
    np.testing.assert_array_equal(result["transactions"], [1, 1, 0, 0, 1, 1])
    assert len(result["labels"]) == len(BAND_LABELS)


def test_band_totals_hand_calculated():
    data = make_data(
        make_row(transaction_id=1, quantity=2, unit_price=100.0, unit_cost=40.0, discount_rate=0.0),
        make_row(transaction_id=2, quantity=4, unit_price=50.0, unit_cost=20.0, discount_rate=0.0),
    )
    result = discount_bands(data, build_metrics(data))
    assert result["units"][0] == 6
    assert result["mean_quantity"][0] == pytest.approx(3.0)
    assert result["revenue"][0] == pytest.approx(400.0)
    assert result["profit"][0] == pytest.approx(240.0)
    assert result["margin_pct"][0] == pytest.approx(60.0)
    assert np.isnan(result["mean_quantity"][1])


def test_perfect_relationship_gives_correlation_one():
    data = make_data(
        make_row(transaction_id=1, quantity=1, discount_rate=0.0),
        make_row(transaction_id=2, quantity=2, discount_rate=0.1),
        make_row(transaction_id=3, quantity=3, discount_rate=0.2),
    )
    result = discount_relationships(data, build_metrics(data))
    assert result["correlation discount vs quantity"] == pytest.approx(1.0)
    assert result["correlation discount vs margin"] < 0


def test_baseline_totals_use_only_rows_with_profit():
    data = make_data(
        make_row(transaction_id=1, quantity=2, unit_price=100.0, unit_cost=40.0, discount_rate=0.1),
        make_row(transaction_id=2, quantity=2, unit_price=100.0, unit_cost=np.nan, discount_rate=0.1),
    )
    totals = baseline_totals(build_metrics(data))
    assert totals["rows"] == 1
    assert totals["gross"] == pytest.approx(200.0)


def test_static_scenario_hand_calculated():
    zero = run_scenario(TOTALS, 0.0)
    assert zero["net_revenue"] == pytest.approx(1000.0)
    assert zero["gross_profit"] == pytest.approx(400.0)
    twenty = run_scenario(TOTALS, 0.20)
    assert twenty["net_revenue"] == pytest.approx(800.0)
    assert twenty["gross_profit"] == pytest.approx(200.0)


def test_demand_response_scenario_hand_calculated():
    result = run_scenario(TOTALS, 0.20, response=0.02)
    assert result["quantity_factor"] == pytest.approx(1.2)
    assert result["net_revenue"] == pytest.approx(960.0)
    assert result["gross_profit"] == pytest.approx(240.0)


def test_scenario_table_changes_against_actual():
    table = scenario_table(TOTALS, [0.0, 0.20], [0.0])
    assert table[0]["profit_change"] == pytest.approx(100.0)
    assert table[0]["profit_change_pct"] == pytest.approx(33.333333)
    assert table[1]["profit_change"] == pytest.approx(-100.0)


def test_percent_change_with_zero_baseline_is_nan():
    assert np.isnan(percent_change(5.0, 0.0))


def test_breakeven_quantity_change():
    assert breakeven_quantity_change(TOTALS, 0.0) == pytest.approx(-25.0)
    assert breakeven_quantity_change(TOTALS, 0.20) == pytest.approx(50.0)


def test_breakeven_is_nan_when_scenario_has_no_profit():
    assert np.isnan(breakeven_quantity_change(TOTALS, 0.50))