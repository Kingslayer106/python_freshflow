import time

from freshflow.pipeline import run_pipeline

start = time.perf_counter()
results = run_pipeline("data/raw/freshflow_sales.csv", "data/processed")
elapsed = time.perf_counter() - start

summary = results["summary"]
print("Raw rows:", results["raw_rows"])
print("Clean rows:", results["clean_rows"])
print("Excluded rows:", results["excluded_rows"])
print("Net revenue:", round(summary["net revenue"], 2))
print("Gross profit:", round(summary["gross profit"], 2))
print("Gross margin %:", round(summary["gross margin %"], 2))
print("Flagged rows in exception register:", results["anomaly_rows"])
print("Runtime (seconds):", round(elapsed, 2))