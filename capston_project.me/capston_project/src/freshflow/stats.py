import numpy as np

from freshflow.metrics import margin_pct
from freshflow.validation import column

OUTLET_NAMES = {1: "Outlet A", 2: "Outlet B", 3: "Outlet C"}

PRODUCT_NAMES = {
    1: "Orange Juice", 2: "Mango Juice", 3: "Apple Juice", 4: "Watermelon Juice",
    5: "Banana Smoothie", 6: "Mixed Fruit Smoothie", 7: "Lemonade", 8: "Iced Tea",
}

CATEGORY_NAMES = {1: "Juice", 2: "Smoothie", 3: "Lemonade", 4: "Tea"}


def skewness(values):
    centered = values - values.mean()
    return np.mean(centered ** 3) / np.mean(centered ** 2) ** 1.5


def describe(values):
    values = values[np.isfinite(values)]
    q1, median, q3 = np.percentile(values, [25, 50, 75])
    return {
        "count": len(values),
        "mean": values.mean(),
        "median": median,
        "std (sample)": values.std(ddof=1),
        "min": values.min(),
        "q1": q1,
        "q3": q3,
        "max": values.max(),
        "range": np.ptp(values),
        "skewness": skewness(values),
    }


def iqr_fences(values):
    values = values[np.isfinite(values)]
    q1, q3 = np.percentile(values, [25, 75])
    spread = q3 - q1
    return q1 - 1.5 * spread, q3 + 1.5 * spread


def histogram_table(values, bins=10):
    values = values[np.isfinite(values)]
    counts, edges = np.histogram(values, bins=bins)
    return counts, edges


def group_sum(codes, values, valid, size):
    return np.bincount(codes[valid].astype(int), weights=values[valid], minlength=size)


def group_performance(data, metrics, group_name):
    codes = column(data, group_name)
    size = int(codes.max()) + 1
    keys = np.unique(codes).astype(int)

    quantity = column(data, "quantity")
    all_rows = np.ones(len(codes), dtype=bool)
    revenue_rows = ~np.isnan(metrics["net_revenue"])
    profit_rows = ~np.isnan(metrics["gross_profit"])

    units = group_sum(codes, quantity, all_rows, size)[keys]
    revenue = group_sum(codes, metrics["net_revenue"], revenue_rows, size)[keys]
    profit = group_sum(codes, metrics["gross_profit"], profit_rows, size)[keys]
    profit_revenue = group_sum(codes, metrics["net_revenue"], profit_rows, size)[keys]

    return {
        "keys": keys,
        "units": units,
        "revenue": revenue,
        "profit": profit,
        "margin_pct": margin_pct(profit, profit_revenue),
        "revenue_share_pct": revenue / revenue.sum() * 100,
    }


def ranking(result, field):
    return result["keys"][np.argsort(result[field])[::-1]]