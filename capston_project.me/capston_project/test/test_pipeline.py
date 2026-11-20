from pathlib import Path

import numpy as np
import pytest

from freshflow.loader import COLUMNS, load_sales, save_array
from freshflow.pipeline import run_pipeline
from freshflow.validation import CATEGORY_OF_PRODUCT

ROWS = 400


def make_synthetic_sales():
    rng = np.random.default_rng(42)
    product = rng.integers(1, 9, ROWS)
    price = rng.uniform(20, 130, ROWS).round(2)
    data = np.column_stack((
        np.arange(1, ROWS + 1),
        rng.integers(1, 31, ROWS),
        rng.integers(1, 4, ROWS),
        product,
        [CATEGORY_OF_PRODUCT[code] for code in product],
        rng.integers(1, 6, ROWS),
        price,
        (price * 0.5).round(2),
        rng.choice([0, 0.05, 0.10, 0.15, 0.20], ROWS),
        rng.integers(10, 50, ROWS),
        rng.integers(1, 5, ROWS),
        rng.integers(1, 6, ROWS),
    )).astype(float)
    data[:30, 1] = np.arange(1, 31)
    data[5, 5] = -1
    data[10, 6] = np.nan
    return data


def test_pipeline_runs_and_saves_files(tmp_path):
    raw_path = tmp_path / "sales.csv"
    save_array(raw_path, make_synthetic_sales())

    results = run_pipeline(raw_path, tmp_path / "processed", expected_rows=ROWS)

    assert results["raw_rows"] == ROWS
    assert results["clean_rows"] + results["excluded_rows"] == ROWS
    assert results["excluded_rows"] == 1
    for name in [
        "freshflow_clean.csv", "freshflow_clean_with_metrics.csv", "freshflow_invalid_records.csv",
        "freshflow_exception_register.csv", "freshflow_daily_trend.csv", "cleaning_report.txt",
    ]:
        assert (tmp_path / "processed" / name).exists()


def test_pipeline_does_not_change_raw_file(tmp_path):
    raw_path = tmp_path / "sales.csv"
    save_array(raw_path, make_synthetic_sales())
    before = raw_path.read_text()
    run_pipeline(raw_path, tmp_path / "processed", expected_rows=ROWS)
    assert raw_path.read_text() == before


def test_saved_clean_file_loads_back(tmp_path):
    raw_path = tmp_path / "sales.csv"
    save_array(raw_path, make_synthetic_sales())
    results = run_pipeline(raw_path, tmp_path / "processed", expected_rows=ROWS)
    clean = load_sales(tmp_path / "processed" / "freshflow_clean.csv", expected_rows=None)
    assert clean.shape == (results["clean_rows"], len(COLUMNS))


REAL_FILE = Path("data/raw/freshflow_sales.csv")


@pytest.mark.skipif(not REAL_FILE.exists(), reason="real dataset not found")
def test_real_dataset_counts(tmp_path):
    results = run_pipeline(REAL_FILE, tmp_path)
    assert results["raw_rows"] == 5000
    assert results["excluded_rows"] == 15
    assert results["clean_rows"] == 4985
    assert results["summary"]["net revenue"] == pytest.approx(1105205.25, abs=0.01)