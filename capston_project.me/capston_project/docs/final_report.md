# FreshFlow Juice Company: NumPy Data Analyst Report

Prepared by: Mohd Shuaib (Junior Data Analyst)
Dataset: `freshflow_sales.csv`, 5000 transactions, 3 outlets, 30 days
Method: Python and NumPy only for loading, cleaning, metrics, statistics and scenarios

---

## 1. Executive summary

### Three findings

1. **Discounts lower margin and show no quantity benefit in this data.** Gross margin falls from 47.04% on undiscounted sales to 34.43% on sales with a 15% to 20% discount. Average quantity per transaction stays between 2.9 and 3.05 in every discount band, and the correlation between discount and quantity is 0.005.
2. **Outlet differences come from the number of transactions, and product differences come from price.** Outlet A has 1,981 transactions, Outlet B 1,733 and Outlet C 1,267, while the average transaction value (about 221 to 224 INR) and the margin (about 44%) are almost the same. Product unit volumes are close (1,771 to 1,912), but smoothies earn 37.7% of net revenue from 23.9% of units.
3. **A small share of records is unreliable or needs review.** 15 of 5,000 rows (0.3%) were excluded as invalid, 157 clean rows are flagged for review, five sales carry a 90% discount, and five sales happened with zero recorded stock.

### Three recommendations

1. Test a reduction of discounts of 15% and above at one outlet and track margin and quantity per transaction.
2. Investigate why Outlet C records 36% fewer transactions than Outlet A.
3. Add input rules at the point of sale and review the flagged exceptions (90% discounts, zero-stock sales, repeated transaction IDs).

Details, owners and metrics are in section 11.

---

## 2. Dataset profile

| Item | Value |
|---|---|
| Source | `freshflow_sales.csv` (synthetic learning dataset with deliberately injected defects) |
| Grain | One row per transaction |
| Size | 5000 data rows, 12 numeric columns (verified by an assertion in the loader) |
| Period | `day_index` 1 to 30. No calendar dates are given, so weekday comparison is not possible |
| Coverage | 3 outlets, 8 products, 4 categories, 4 payment methods |
| Currency | INR |
| Loading | `np.genfromtxt` with `delimiter=","`, `skip_header=1`, `ndmin=2`. Blank cells load as NaN |

Assumptions: the discount applies to the full line; cost is direct product cost only; gross profit excludes rent, payroll and other operating expenses.

---

## 3. Data quality

The raw file is never changed. Cleaning works on a copy and every decision is written to `cleaning_report.txt`.

| Issue | Target | Observed | Treatment |
|---|---|---|---|
| Missing unit_price | 4 | 4 | Kept. Revenue and profit are unavailable for these rows. No imputation |
| Missing unit_cost | 4 | 4 | Kept. Profit is unavailable for these rows |
| Missing customer_rating | 20 | 20 | Kept. Ignored only in the rating mean (never treated as zero) |
| Duplicate transaction IDs | 5 records | 5 records (ID 1789 three times, ID 4039 twice) | Kept and flagged. Day, outlet and product differ, so these are different sales with a colliding ID |
| Zero or negative quantity | 4 | 4 | Excluded. Refund or error cannot be told apart from the data, so they are not completed sales |
| Negative unit_price | 2 | 2 | Excluded |
| Negative unit_cost | 2 | 2 | Excluded |
| Discount rate above 1 | 2 | 2 | Excluded |
| Invalid customer rating | 3 | 3 | Rating set to NaN, sale kept |
| Product and category mismatch | 4 | 3 | Excluded. Observed count is one lower than the target and is reported as observed |
| Unknown outlet code | 2 | 2 | Excluded |
| High but valid price | 3 | 3 | Flagged, kept |
| High but valid discount | 5 | 5 (all at 90%) | Flagged, kept |
| Zero stock before sale | 5 | 5 | Flagged, kept |

Summary of counts:

| Measure | Count |
|---|---|
| Total rule violations (invalid rules) | 23 |
| Unique rows affected | 23 (no row breaks two rules) |
| Rows excluded | 15 |
| Ratings set to NaN | 3 |
| Rows kept with a collision flag | 5 |
| Raw rows | 5,000 |
| Clean rows | 4,985 (99.7%) |

Excluded rows are saved in `freshflow_invalid_records.csv` with a reason code, so no evidence is lost.

---

## 4. Metric definitions

| Metric | Formula | Denominator or guardrail |
|---|---|---|
| Gross sales | quantity x unit_price | Rows with a price |
| Discount amount | gross sales x discount rate | |
| Net revenue | gross sales - discount amount | 4,981 rows have revenue |
| Cost of goods sold | quantity x unit_cost | Rows with a cost |
| Gross profit | net revenue - COGS | 4,977 rows have profit |
| Gross margin % | total gross profit / total net revenue x 100 | Same 4,977 rows in numerator and denominator |
| Weighted discount % | total discount / total gross sales x 100 | Rows with revenue |
| Average transaction value | total net revenue / number of rows with revenue | 4,981 |
| Average selling price | net revenue / quantity | Only when quantity is above 0 |

Margin is never calculated as the average of row margins. Units sold are counted over all 4,985 clean rows because quantity is valid even where price is missing.

---

## 5. Sales performance

Overall (clean data):

| Measure | Value |
|---|---|
| Gross sales | 1,174,854.49 |
| Discount amount | 69,649.24 |
| Net revenue | 1,105,205.25 |
| Gross profit | 484,553.14 |
| Gross margin | 43.87% |
| Weighted discount | 5.93% |
| Units sold | 14,837 |
| Mean customer rating | 2.97 (4,962 valid ratings) |

### Outlets

| Outlet | Transactions | Units | Net revenue | Gross profit | Margin | Revenue share | Average transaction value |
|---|---|---|---|---|---|---|---|
| A | 1,981 | 5,837 | 439,003 | 192,087 | 43.79% | 39.72% | 221.61 |
| B | 1,733 | 5,169 | 382,964 | 168,360 | 44.00% | 34.65% | 220.98 |
| C | 1,267 | 3,831 | 283,238 | 124,106 | 43.84% | 25.63% | 223.55 |

Outlet A ranks first on revenue, gross profit and units. Margin and average transaction value are almost equal across outlets, so the gap is explained by how many transactions each outlet records.

### Products

| Product | Units | Net revenue | Gross profit | Margin | Median price |
|---|---|---|---|---|---|
| Mixed Fruit Smoothie | 1,771 | 216,258 | 94,820 | 43.85% | 130.06 |
| Banana Smoothie | 1,775 | 199,911 | 86,965 | 43.57% | 120.29 |
| Mango Juice | 1,881 | 158,118 | 68,763 | 43.49% | 89.88 |
| Orange Juice | 1,872 | 141,567 | 62,166 | 43.91% | 80.00 |
| Apple Juice | 1,845 | 121,674 | 54,052 | 44.59% | 69.86 |
| Watermelon Juice | 1,912 | 107,429 | 47,099 | 43.84% | 60.24 |
| Lemonade | 1,901 | 89,605 | 39,739 | 44.37% | 50.05 |
| Iced Tea | 1,880 | 70,643 | 30,950 | 43.81% | 40.00 |

Revenue and gross profit give the same product order. Watermelon Juice sells the most units (1,912) but is sixth on revenue. Mixed Fruit Smoothie sells the fewest units (1,771) but is first on profit. Units are almost equal across products and margins are close (43.5% to 44.6%), so the difference comes from price per unit, not from volume or margin.

### Categories

| Category | Units | Net revenue | Revenue share | Margin |
|---|---|---|---|---|
| Juice | 7,510 | 528,787 | 47.85% | 43.93% |
| Smoothie | 3,546 | 416,169 | 37.66% | 43.71% |
| Lemonade | 1,901 | 89,605 | 8.11% | 44.37% |
| Tea | 1,880 | 70,643 | 6.39% | 43.81% |

### Distribution of transaction value (net revenue)

| Statistic | Value |
|---|---|
| Mean | 221.88 |
| Median | 195.36 |
| Standard deviation (sample) | 140.17 |
| Q1 / Q3 | 115.43 / 297.73 |
| Maximum | 767.40 |
| Skewness | 0.98 |

The mean is above the median and the skewness is positive, so a minority of large transactions pulls the average up. 146 transactions fall outside the IQR fences (-158.02 and 571.18). They are statistical outliers, not errors, and none was deleted.

---

## 6. Trend analysis

| Measure | Value |
|---|---|
| Total net revenue over 30 days | 1,105,205.25 |
| Highest day | Day 7 (42,714) |
| Lowest day | Day 3 (31,708) |
| Average revenue, days 1 to 15 | 36,828.57 |
| Average revenue, days 16 to 30 | 36,851.78 |
| Days with an unusual change (z-score above 2) | None |

The largest day-to-day moves were Day 3 (down 25.1%, z = -1.99) and Day 8 (down 22.4%, z = -1.79). Day-to-day swings of up to about 25% are common, but no single day stands out statistically, and the two halves of the month have almost the same average. The data shows no upward or downward trend.

A 30-day window cannot support annual seasonality claims. Weekday patterns cannot be studied because the data has day numbers but no dates.

---

## 7. Discount and profitability analysis

| Discount band | Transactions | Average quantity | Net revenue | Gross profit | Margin |
|---|---|---|---|---|---|
| 0% | 2,254 | 2.97 | 533,751 | 251,055 | 47.04% |
| above 0 to 5% | 958 | 2.99 | 218,435 | 96,979 | 44.40% |
| above 5 to 10% | 791 | 2.95 | 163,659 | 67,524 | 41.26% |
| above 10 to 15% | 591 | 3.05 | 119,482 | 46,001 | 38.50% |
| above 15 to 20% | 378 | 2.92 | 68,897 | 23,720 | 34.43% |
| above 20% | 5 | 3.40 | 174 | -725 | -418.13% |

Bands use the 4,977 rows that have a profit value.

- Correlation between discount and quantity: **0.005**. Higher discounts are not accompanied by larger quantities in this data.
- Correlation between discount and margin: **-0.54**. This is largely arithmetic, because a higher discount lowers revenue and so lowers margin by definition. It is not an independent discovery.

What the data cannot prove: discounts were not assigned randomly, and product, outlet and day may also affect quantity (confounding). The data does not show whether discounts bring new customers or loyalty. Correlation is not causation, so the result is "no association seen", not "discounts do not work".

---

## 8. Anomaly register

Suspicious but valid rows are flagged, not deleted. The full list is in `freshflow_exception_register.csv`, sorted by gross sales (the value of the sale affected). This is exposure, not loss.

| Flag | Rows |
|---|---|
| High price (above 1.5 times the product median) | 3 |
| High discount (above 20%) | 5 |
| Zero stock before the sale | 5 |
| Stock below quantity sold | 5 |
| Net revenue outlier, IQR rule | 146 |
| Net revenue outlier, z-score above 3 | 30 |
| **Unique flagged rows** | **157** |

The flagged rows carry gross sales of 95,308.88 (about 8.1% of all gross sales).

Largest items by gross sales: transaction 300 (day 21, 767.40), transaction 1239 (day 1, 723.70) and transaction 1595 (day 6, 682.45). Transactions 300 and 1239 have a high price as well as outlier revenue.

Items that need a decision:

- **High discount:** five transactions carry a 90% discount. They gave away 1,561.54 of discount (about 2.2% of all discount), produced 173.50 of revenue and a gross loss of 725.48.
- **Zero stock:** five sales (IDs 2107, 2201, 2266, 4022, 4331) happened with zero recorded stock and brought 864.63 of net revenue. All five also have stock below the quantity sold. The transaction file cannot show whether the stock record or the sale is wrong, and no waste or inventory conclusion is made from it.

---

## 9. Scenario analysis

These are scenarios, not forecasts. All scenarios use the same 4,977 rows: gross sales 1,173,949.27, COGS 619,844.48, actual discount 69,551.65 (5.92%), actual net revenue 1,104,397.62 and actual gross profit 484,553.14.

**Static scenario** (quantity and cost held constant, flat discount rate on every row):

| Discount rate | Net revenue | Gross profit | Margin | Profit change | Change % |
|---|---|---|---|---|---|
| 0% | 1,173,949 | 554,105 | 47.20% | +69,552 | +14.35% |
| 5% | 1,115,252 | 495,407 | 44.42% | +10,854 | +2.24% |
| 10% | 1,056,554 | 436,710 | 41.33% | -47,843 | -9.87% |
| 15% | 997,857 | 378,012 | 37.88% | -106,541 | -21.99% |
| 20% | 939,159 | 319,315 | 34.00% | -165,238 | -34.10% |

**Demand-response scenarios** (assumption: each percentage point of discount changes quantity by 1% or 2%; these values are assumptions, not estimates from the data):

| Discount rate | Profit change % (1% per point) | Profit change % (2% per point) |
|---|---|---|
| 0% | +7.58% | +0.80% |
| 5% | +1.29% | +0.35% |
| 10% | -6.20% | -2.53% |
| 15% | -14.91% | -7.83% |
| 20% | -24.83% | -15.55% |

**Break-even quantity change** (change in quantity needed to keep today's profit):

| Discount rate | Quantity change needed |
|---|---|
| 0% | -12.55% |
| 5% | -2.19% |
| 10% | +10.96% |
| 15% | +28.18% |
| 20% | +51.75% |

If discounts were removed, quantity could fall by up to 12.55% before profit dropped below today's level. The data itself shows no quantity lift from discounts.

---

## 10. Limitations

- Gross profit is not net profit. Rent, payroll and other operating expenses are not included.
- Thirty days of data cannot support annual seasonality or long-run business claims.
- Day numbers have no calendar dates, so weekday comparisons are not possible.
- The dataset is synthetic. Findings describe this dataset, not a real business.
- Discount results are associations, not causal effects. Demand-response factors are assumptions.
- 4 rows lack a price and 4 lack a cost, so revenue covers 4,981 rows and profit covers 4,977 rows.
- 15 excluded rows are not in any metric. Excluding zero or negative quantity rows assumes they are not completed sales.
- The product and category mismatch count (3) is below the target (4).
- Inventory waste cannot be analysed from the transaction file. It needs the optional daily operations file.

---

## 11. Recommendations

| # | Action | Owner | Metric to monitor | Follow-up question |
|---|---|---|---|---|
| 1 | Run a controlled test that reduces discounts of 15% and above at one outlet for several weeks | Pricing or commercial manager | Gross margin %, average quantity per transaction, net revenue per day | Does quantity stay level when deep discounts are removed? |
| 2 | Investigate why Outlet C records 36% fewer transactions (1,267 against 1,981 at Outlet A) while basket value and margin match | Operations manager | Daily transactions per outlet | Is the gap caused by foot traffic, opening hours or staffing? |
| 3 | Add point-of-sale rules (quantity above 0, outlet code check, unique ID, discount cap) and review the five 90% discounts and five zero-stock sales | IT or POS owner with the finance team | Invalid row rate (now 0.3%), number of flagged exceptions | Were the 90% discounts approved promotions or entry errors, and is the stock record correct? |

Evidence and limits per recommendation:

1. **Evidence:** margin 47.04% at no discount against 34.43% at 15% to 20%; no quantity lift (correlation 0.005); removing all discounts adds 69,552 of gross profit if quantity holds. **Limit:** association only, and customer loyalty effects are not measured.
2. **Evidence:** the outlet gap is in transaction count, not in value per transaction or margin. **Limit:** the data has no footfall, opening hours or staffing information.
3. **Evidence:** 15 excluded rows, 157 flagged rows, 90% discounts losing 725.48, five zero-stock sales. **Limit:** the transaction file cannot say which record is wrong.

---

## 12. Appendix

### Code layout

```
src/freshflow/   loader, validation, cleaning, metrics, stats, trends,
                 anomalies, scenarios, pipeline
tests/           loader, validation, cleaning, metrics, stats, trends,
                 anomalies, scenarios, pipeline, debugging (69 tests)
notebooks/       01 to 06, one notebook per analysis stage
run_pipeline.py  runs the full workflow in about 0.1 second
```

### How to reproduce

```
pip install -e .
pip install pytest
python run_pipeline.py
pytest
```

### Calculation checks (hand calculation against NumPy output)

| Transaction | Quantity | Price | Cost | Discount | Net revenue | Gross profit | Margin |
|---|---|---|---|---|---|---|---|
| 1 | 1 | 77.75 | 39.95 | 0.05 | 77.75 - 3.8875 = 73.8625 | 73.8625 - 39.95 = 33.9125 | 45.913% |
| 2 | 1 | 50.81 | 32.56 | 0 | 50.81 | 50.81 - 32.56 = 18.25 | 35.918% |
| 3 | 4 | 133.47 | 57.05 | 0 | 533.88 | 533.88 - 228.20 = 305.68 | 57.256% |

The unit tests also check five artificial rows by hand (for example quantity 2, price 100, cost 40, discount 10% gives revenue 180, profit 100 and margin 55.56%), plus tests for NaN values, zero denominators, invalid shapes, views and copies, integer overflow and a loop against the vectorized result.

### Validation assertions in the pipeline

- Clean rows plus excluded rows equal raw rows.
- Gross sales minus discount equals net revenue on every row.
- Daily revenue, and each of the outlet, product and category totals, equal overall net revenue and gross profit.
- Discount band transactions equal the number of rows with profit.
- The cumulative product of daily growth ratios equals revenue divided by day 1 revenue.
- The raw array is unchanged after the run.

### Other documents

- `docs/data_dictionary.md`: columns, units, code mappings and reason codes
- `docs/debugging_notes.md`: documented bug fixes
- `data/processed/cleaning_report.txt`: per-rule counts and treatment
