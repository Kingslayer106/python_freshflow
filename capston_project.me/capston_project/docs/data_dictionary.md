# Data Dictionary (D1)

Source file: `data/raw/freshflow_sales.csv`
Grain: one row per sales transaction. 5000 data rows, 12 columns, 30 consecutive days.
Currency: INR. Every field is numeric; a blank cell means "missing" and is loaded as NaN.

## Columns

| Column | Meaning | Unit | Allowed values | Missing allowed? |
|---|---|---|---|---|
| transaction_id | Transaction identifier | integer | Unique positive integer | No |
| day_index | Observation day | day number | Integer 1 to 30 | No |
| outlet_id | Outlet code | code | 1, 2, 3 | No |
| product_code | Product code | code | 1 to 8 | No |
| category_code | Product category code | code | 1 to 4, must agree with product_code | No |
| quantity | Units sold in the transaction | units | Positive whole number | No |
| unit_price | Selling price per unit | INR | Greater than 0 | Yes (recorded as a data-quality issue) |
| unit_cost | Direct cost per unit | INR | 0 or greater | Yes (recorded as a data-quality issue) |
| discount_rate | Discount as a fraction of gross sales | fraction | 0 to 1 inclusive (0.15 means 15%) | No |
| stock_before_units | Recorded available units before the sale | units | 0 or greater | No |
| payment_code | Payment method code | code | 1 to 4 | No |
| customer_rating | Customer rating | score | 1 to 5 | Yes (missing is normal) |

## Code dictionaries

| Outlet code | Meaning |
|---|---|
| 1 | Outlet A |
| 2 | Outlet B |
| 3 | Outlet C |

| Product code | Product | Category code |
|---|---|---|
| 1 | Orange Juice | 1 |
| 2 | Mango Juice | 1 |
| 3 | Apple Juice | 1 |
| 4 | Watermelon Juice | 1 |
| 5 | Banana Smoothie | 2 |
| 6 | Mixed Fruit Smoothie | 2 |
| 7 | Lemonade | 3 |
| 8 | Iced Tea | 4 |

| Category code | Meaning |
|---|---|
| 1 | Juice |
| 2 | Smoothie |
| 3 | Lemonade |
| 4 | Tea |

| Payment code | Meaning |
|---|---|
| 1 | Cash |
| 2 | UPI |
| 3 | Card |
| 4 | Other digital payment |

## Derived metrics

| Metric | Formula | Guardrail |
|---|---|---|
| Gross sales | quantity x unit_price | NaN if price is missing |
| Discount amount | gross_sales x discount_rate | |
| Net revenue | gross_sales - discount_amount | Discount applies to the full line |
| Cost of goods sold | quantity x unit_cost | NaN if cost is missing |
| Gross profit | net_revenue - cogs | Before rent, payroll and other operating expenses |
| Gross margin % | gross_profit / net_revenue x 100 | NaN when net revenue is 0 |
| Average selling price | net_revenue / quantity | Only when quantity is greater than 0 |
| Overall margin % | total gross profit / total net revenue x 100 | Never the average of row margins |

## Files created by the pipeline (`data/processed/`)

| File | Content |
|---|---|
| freshflow_clean.csv | Rows kept after cleaning (12 columns) |
| freshflow_clean_with_metrics.csv | Clean rows plus the 7 derived metric columns |
| freshflow_invalid_records.csv | Excluded rows plus a `reason_code` column |
| freshflow_exception_register.csv | Suspicious but valid rows, with a bit-flag `reason_code` |
| freshflow_daily_trend.csv | 30-day revenue table with changes, 7-day average and cumulative revenue |
| cleaning_report.txt | Per-rule counts, treatment and the reason code legend |

## Exception register reason codes

The code is the sum of these weights.

| Weight | Flag |
|---|---|
| 1 | High price (more than 1.5 times the product median price) |
| 2 | High discount (above 20% and up to 100%) |
| 4 | Zero stock before the sale |
| 8 | Stock below the quantity sold |
| 16 | Net revenue outlier by the IQR rule |
| 32 | Net revenue outlier by the z-score rule (above 3) |

Example: 49 = 1 + 16 + 32 = high price, IQR outlier and z-score outlier.
