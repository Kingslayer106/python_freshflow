import numpy as np

from freshflow.loader import COL
from freshflow.stats import iqr_fences
from freshflow.validation import column

REGISTER_COLUMNS = [
    "transaction_id", "day_index", "outlet_id", "product_code", "quantity",
    "unit_price", "discount_rate", "stock_before_units", "gross_sales", "reason_code",
]


def high_price_mask(data):
    product = column(data, "product_code")
    price = column(data, "unit_price")
    mask = np.zeros(len(data), dtype=bool)
    for code in np.unique(product):
        same_product = product == code
        mask[same_product] = price[same_product] > 1.5 * np.nanmedian(price[same_product])
    return mask


def revenue_outlier_masks(revenue):
    low, high = iqr_fences(revenue)
    valid = revenue[np.isfinite(revenue)]
    with np.errstate(divide="ignore", invalid="ignore"):
        z_scores = (revenue - valid.mean()) / valid.std(ddof=1)
    return (revenue < low) | (revenue > high), np.abs(z_scores) > 3


def anomaly_masks(data, metrics):
    discount = column(data, "discount_rate")
    stock = column(data, "stock_before_units")
    quantity = column(data, "quantity")
    iqr_flag, z_flag = revenue_outlier_masks(metrics["net_revenue"])

    return {
        "high price": high_price_mask(data),
        "high discount": (discount > 0.20) & (discount <= 1),
        "zero stock": stock == 0,
        "stock below quantity": stock < quantity,
        "IQR revenue outlier": iqr_flag,
        "z-score revenue outlier": z_flag,
    }


def reason_codes(masks):
    table = np.vstack(list(masks.values())).astype(int)
    weights = 2 ** np.arange(len(masks))
    return weights @ table


def reason_text(code, names):
    return ", ".join(name for position, name in enumerate(names) if code // 2 ** position % 2)


def exception_register(data, metrics, masks):
    codes = reason_codes(masks)
    rows = np.nonzero(codes > 0)[0]
    impact = metrics["gross_sales"][rows]

    order = np.argsort(np.nan_to_num(impact, nan=-1))[::-1]
    rows = rows[order]

    kept_columns = [COL[name] for name in REGISTER_COLUMNS[:8]]
    return np.column_stack((data[rows][:, kept_columns], impact[order], codes[rows]))