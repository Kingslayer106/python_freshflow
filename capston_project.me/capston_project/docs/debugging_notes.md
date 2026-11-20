# Debugging notes

## Bug 1: clean file could not be loaded (shape error)

Symptom: load_sales("freshflow_clean.csv") stopped with
AssertionError: Unexpected shape: (4985, 12)

Cause: load_sales always asserted exactly 5000 rows. That is right for the raw
file, but the clean file has 4985 rows after 15 invalid rows were excluded.

Fix: added the expected_rows parameter. The raw file keeps the default of 5000,
and load_sales(path, expected_rows=None) skips the row check for derived files.

Regression tests: test_wrong_row_count_raises_assertion and
test_expected_rows_none_skips_the_row_check in tests/test_loader.py.

## Bug 2: RuntimeWarning "invalid value in divide" in the z-score

Symptom: warning when all revenue values are equal (standard deviation is 0).

Cause: (x - mean) / std divides by zero.

Fix: wrapped the division in np.errstate and kept the comparison rule, because
a NaN z-score compares as False and is never flagged.

## Bug 3: saved numbers lost decimals

Symptom: cumulative revenue in the daily trend file looked like 1.1052e+06.

Cause: np.savetxt with fmt="%g" keeps only 6 significant digits.

Fix: save_array now takes a fmt argument and the trend table uses "%.2f".
