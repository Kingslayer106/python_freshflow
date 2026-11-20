import numpy as np

from freshflow.metrics import margin_pct, safe_divide
from freshflow.stats import group_sum
from freshflow.validation import column

BAND_EDGES = [0, 0.05, 0.10, 0.15, 0.20]
BAND_LABELS = ["0%", ">0 to 5%", ">5 to 10%", ">10 to 15%", ">15 to 20%", ">20%"]


def discount_bands(data, metrics):
    rate = column(data, "discount_rate")
    quantity = column(data, "quantity")
    valid = ~np.isnan(metrics["gross_profit"])
    band = np.digitize(rate, BAND_EDGES, right=True)
    size = len(BAND_LABELS)

    transactions = np.bincount(band[valid], minlength=size)
    units = group_sum(band, quantity, valid, size)
    revenue = group_sum(band, metrics["net_revenue"], valid, size)
    profit = group_sum(band, metrics["gross_profit"], valid, size)

    with np.errstate(divide="ignore", invalid="ignore"):
        mean_quantity = np.where(transactions > 0, units / transactions, np.nan)

    return {
        "labels": BAND_LABELS,
        "transactions": transactions,
        "units": units,
        "mean_quantity": mean_quantity,
        "revenue": revenue,
        "profit": profit,
        "margin_pct": margin_pct(profit, revenue),
    }


def discount_relationships(data, metrics):
    rate = column(data, "discount_rate")
    quantity = column(data, "quantity")
    margin = metrics["margin_pct"]
    valid = np.isfinite(margin)

    return {
        "rows used": int(valid.sum()),
        "correlation discount vs quantity": np.corrcoef(rate[valid], quantity[valid])[0, 1],
        "correlation discount vs margin": np.corrcoef(rate[valid], margin[valid])[0, 1],
        "covariance discount vs quantity": np.cov(rate[valid], quantity[valid])[0, 1],
    }


def baseline_totals(metrics):
    rows = ~np.isnan(metrics["gross_profit"])
    return {
        "rows": int(rows.sum()),
        "gross": metrics["gross_sales"][rows].sum(),
        "cogs": metrics["cogs"][rows].sum(),
        "discount": metrics["discount_amount"][rows].sum(),
    }


def percent_change(new, base):
    return (new - base) / base * 100 if base != 0 else np.nan


def actual_results(totals):
    revenue = totals["gross"] - totals["discount"]
    return revenue, revenue - totals["cogs"]


def run_scenario(totals, rate, response=0.0):
    baseline_rate = safe_divide(totals["discount"], totals["gross"])
    factor = 1 + response * (rate - baseline_rate) * 100
    revenue = totals["gross"] * (1 - rate) * factor
    profit = revenue - totals["cogs"] * factor
    return {
        "rate": rate,
        "response": response,
        "quantity_factor": factor,
        "net_revenue": revenue,
        "gross_profit": profit,
        "margin_pct": safe_divide(profit, revenue) * 100,
    }


def scenario_table(totals, rates, responses):
    actual_revenue, actual_profit = actual_results(totals)
    table = []
    for response in responses:
        for rate in rates:
            result = run_scenario(totals, rate, response)
            result["revenue_change"] = result["net_revenue"] - actual_revenue
            result["revenue_change_pct"] = percent_change(result["net_revenue"], actual_revenue)
            result["profit_change"] = result["gross_profit"] - actual_profit
            result["profit_change_pct"] = percent_change(result["gross_profit"], actual_profit)
            table.append(result)
    return table


def breakeven_quantity_change(totals, rate):
    _, actual_profit = actual_results(totals)
    profit_per_full_quantity = totals["gross"] * (1 - rate) - totals["cogs"]
    if profit_per_full_quantity <= 0:
        return np.nan
    return (actual_profit / profit_per_full_quantity - 1) * 100