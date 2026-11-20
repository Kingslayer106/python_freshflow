# FreshFlow NumPy Data Analyst Project

End-to-end analysis of 5000 juice-outlet transactions using Python and NumPy only.

The workflow is: inspect, validate, clean, calculate metrics, compare groups, find trends and anomalies, test discount scenarios, and report.

## Setup

```
pip install -e .
pip install pytest
```

## Run

Put the dataset at `data/raw/freshflow_sales.csv`, then from the project root:

```
python run_pipeline.py
```

This writes six files to `data/processed/` and prints a short summary.

## Test

```
pytest
```

## Structure

```
capstone_project/
├── data/
│   ├── raw/                 original CSV, never edited
│   └── processed/           clean data, invalid rows, exception register, daily trend, cleaning report
├── notebooks/               01 load and profile
│                            02 validation and cleaning
│                            03 metrics and statistics
│                            04 trend and anomalies
│                            05 discount scenarios
│                            06 final analysis
├── src/freshflow/           loader, validation, cleaning, metrics, stats,
│                            trends, anomalies, scenarios, pipeline
├── tests/                   unit and pipeline tests
├── docs/                    data dictionary, final report, debugging notes
├── dataset_generation.py    creates the synthetic dataset
├── run_pipeline.py          runs the full workflow
├── pyproject.toml
├── pytest.ini
└── requirements.txt
```

## Documents

- `docs/data_dictionary.md`: columns, units, code mappings
- `docs/final_report.md`: findings, recommendations and limitations
- `docs/debugging_notes.md`: documented bug fixes

## Key rules followed

- The raw file is never changed. Cleaning works on a copy.
- Invalid rows are excluded but saved with a reason code.
- Suspicious but valid rows are flagged, not deleted.
- Missing ratings are never treated as zero, and prices or costs are never imputed.
- Overall margin is total profit divided by total revenue over the same rows.
- Scenarios are labelled as scenarios, not forecasts.
