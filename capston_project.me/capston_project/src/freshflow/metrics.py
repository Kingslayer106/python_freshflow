import numpy as np

from freshflow.validation import column


def gross_sales(quantity, price):
    return quantity * price


def discount_amount(gross, rate):
    return gross * rate


def net_revenue(gross, discount):
    return gross - discount


def cost_of_goods_sold(quantity, cost):
    return quantity * cost


def gross_profit(revenue, cogs):
    return revenue - cogs


def margin_pct(profit, revenue):
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(revenue != 0, profit / revenue * 100, np.nan)


def average_selling_price(revenue, quantity):
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(quantity > 0, revenue / quantity, np.nan)


def safe_divide(top, bottom):
    return top / bottom if bottom != 0 else np.nan


def build_metrics(data):
    quantity = column(data, "quantity")
    price = column(data, "unit_price")
    cost = column(data, "unit_cost")
    rate = column(data, "discount_rate")

    gross = gross_sales(quantity, price)
    discount = discount_amount(gross, rate)
    revenue = net_revenue(gross, discount)
    cogs = cost_of_goods_sold(quantity, cost)
    profit = gross_profit(revenue, cogs)

    return {
        "gross_sales": gross,
        "discount_amount": discount,
        "net_revenue": revenue,
        "cogs": cogs,
        "gross_profit": profit,
        "margin_pct": margin_pct(profit, revenue),
        "avg_selling_price": average_selling_price(revenue, quantity),
    }


def summarize(data, metrics):
    revenue_rows = ~np.isnan(metrics["net_revenue"])
    profit_rows = ~np.isnan(metrics["gross_profit"])
    rating = column(data, "customer_rating")

    gross = metrics["gross_sales"][revenue_rows].sum()
    discount = metrics["discount_amount"][revenue_rows].sum()
    revenue = metrics["net_revenue"][revenue_rows].sum()
    cogs = metrics["cogs"][profit_rows].sum()
    profit = metrics["gross_profit"][profit_rows].sum()
    profit_revenue = metrics["net_revenue"][profit_rows].sum()

    return {
        "rows with revenue": int(revenue_rows.sum()),
        "rows with profit": int(profit_rows.sum()),
        "gross sales": gross,
        "discount amount": discount,
        "net revenue": revenue,
        "cogs": cogs,
        "gross profit": profit,
        "gross margin %": safe_divide(profit, profit_revenue) * 100,
        "weighted discount %": safe_divide(discount, gross) * 100,
        "average transaction value": safe_divide(revenue, revenue_rows.sum()),
        "units sold": column(data, "quantity").sum(),
        "valid rating count": int(np.isfinite(rating).sum()),
        "mean rating": np.nanmean(rating),
    }