from pathlib import Path

import numpy as np

from freshflow.anomalies import REGISTER_COLUMNS, anomaly_masks, exception_register, reason_codes
from freshflow.cleaning import clean_data, write_cleaning_report
from freshflow.loader import COLUMNS, EXPECTED_ROWS, load_sales, save_array
from freshflow.metrics import build_metrics, summarize
from freshflow.scenarios import baseline_totals, discount_bands, scenario_table
from freshflow.stats import group_performance
from freshflow.trends import daily_change, daily_pct_change, daily_totals, rolling_average

METRIC_COLUMNS = [
    "gross_sales", "discount_amount", "net_revenue", "cogs",
    "gross_profit", "margin_pct", "avg_selling_price",
]

TREND_COLUMNS = [
    "day", "transactions", "revenue", "change",
    "change_pct", "rolling_7_day_avg", "cumulative_revenue",
]

SCENARIO_RATES = [0, 0.05, 0.10, 0.15, 0.20]
SCENARIO_RESPONSES = [0.0, 0.01, 0.02]


def trend_table(revenue, transactions):
    days = np.arange(1, len(revenue) + 1)
    change = np.concatenate(([np.nan], daily_change(revenue)))
    change_pct = np.concatenate(([np.nan], daily_pct_change(revenue)))
    return np.stack(
        (days, transactions, revenue, change, change_pct, rolling_average(revenue), np.cumsum(revenue)),
        axis=1,
    )


def validate_results(raw, clean, excluded, metrics, summary, revenue, groups, bands, register, masks):
    assert len(clean) + len(excluded) == len(raw)

    for values in metrics.values():
        assert len(values) == len(clean)

    valid = ~np.isnan(metrics["net_revenue"])
    np.testing.assert_allclose(
        metrics["gross_sales"][valid] - metrics["discount_amount"][valid],
        metrics["net_revenue"][valid],
    )

    np.testing.assert_allclose(revenue.sum(), summary["net revenue"])
    for result in groups.values():
        np.testing.assert_allclose(result["revenue"].sum(), summary["net revenue"])
        np.testing.assert_allclose(result["profit"].sum(), summary["gross profit"])

    assert bands["transactions"].sum() == summary["rows with profit"]
    assert len(register) == int((reason_codes(masks) > 0).sum())

    if np.all(revenue > 0):
        growth = 1 + daily_pct_change(revenue) / 100
        np.testing.assert_allclose(np.cumprod(growth), revenue[1:] / revenue[0])


def run_pipeline(raw_path, processed_dir, expected_rows=EXPECTED_ROWS):
    processed_dir = Path(processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)

    raw = load_sales(raw_path, expected_rows=expected_rows)
    raw_copy = raw.copy()

    clean, excluded, clean_masks, exclude = clean_data(raw)
    metrics = build_metrics(clean)
    summary = summarize(clean, metrics)

    groups = {
        "outlet": group_performance(clean, metrics, "outlet_id"),
        "product": group_performance(clean, metrics, "product_code"),
        "category": group_performance(clean, metrics, "category_code"),
    }

    revenue, transactions = daily_totals(clean, metrics)
    bands = discount_bands(clean, metrics)
    masks = anomaly_masks(clean, metrics)
    register = exception_register(clean, metrics, masks)
    scenarios = scenario_table(baseline_totals(metrics), SCENARIO_RATES, SCENARIO_RESPONSES)

    validate_results(raw, clean, excluded, metrics, summary, revenue, groups, bands, register, masks)
    np.testing.assert_array_equal(raw, raw_copy)

    metric_values = np.stack([metrics[name] for name in METRIC_COLUMNS], axis=1)
    save_array(processed_dir / "freshflow_clean.csv", clean)
    save_array(processed_dir / "freshflow_clean_with_metrics.csv", np.hstack((clean, metric_values)), COLUMNS + METRIC_COLUMNS)
    save_array(processed_dir / "freshflow_invalid_records.csv", excluded, COLUMNS + ["reason_code"])
    save_array(processed_dir / "freshflow_exception_register.csv", register, REGISTER_COLUMNS)
    save_array(processed_dir / "freshflow_daily_trend.csv", trend_table(revenue, transactions), TREND_COLUMNS, fmt="%.2f")
    write_cleaning_report(processed_dir / "cleaning_report.txt", clean_masks, exclude, len(raw))

    return {
        "raw_rows": len(raw),
        "clean_rows": len(clean),
        "excluded_rows": len(excluded),
        "summary": summary,
        "groups": groups,
        "daily_revenue": revenue,
        "bands": bands,
        "anomaly_rows": len(register),
        "scenarios": scenarios,
    }