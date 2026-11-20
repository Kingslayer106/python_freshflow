import numpy as np

from freshflow.stats import group_sum
from freshflow.validation import column

DAYS = 30


def daily_totals(data, metrics, days=DAYS):
    day = column(data, "day_index").astype(int)
    has_revenue = ~np.isnan(metrics["net_revenue"])
    revenue = group_sum(day, metrics["net_revenue"], has_revenue, days + 1)[1:]
    transactions = np.bincount(day[has_revenue], minlength=days + 1)[1:]
    return revenue, transactions


def daily_change(revenue):
    return np.diff(revenue)


def daily_pct_change(revenue):
    previous = revenue[:-1]
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(previous != 0, np.diff(revenue) / previous * 100, np.nan)


def rolling_average(values, window=7):
    averages = np.convolve(values, np.ones(window) / window, mode="valid")
    return np.concatenate((np.full(window - 1, np.nan), averages))


def unusual_changes(revenue, threshold=2):
    change = np.diff(revenue)
    spread = change.std(ddof=1)
    if spread == 0:
        return np.zeros(len(change)), np.zeros(len(change), dtype=bool)
    z_scores = (change - change.mean()) / spread
    return z_scores, np.abs(z_scores) > threshold