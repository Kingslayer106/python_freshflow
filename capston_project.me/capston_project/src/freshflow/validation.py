import numpy as np

from freshflow.loader import COL

CATEGORY_OF_PRODUCT = {1: 1, 2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3, 8: 4}


def column(data, name):
    return data[:, COL[name]]


def is_whole(values):
    with np.errstate(invalid="ignore"):
        return np.isfinite(values) & (values % 1 == 0)


def duplicate_id_mask(ids):
    unique_ids, counts = np.unique(ids, return_counts=True)
    repeated_ids = unique_ids[counts > 1]
    return np.isin(ids, repeated_ids)


def expected_category(products):
    expected = np.full(products.shape, np.nan)
    for product, category in CATEGORY_OF_PRODUCT.items():
        expected[products == product] = category
    return expected


def invalid_masks(data):
    ids = column(data, "transaction_id")
    day = column(data, "day_index")
    outlet = column(data, "outlet_id")
    product = column(data, "product_code")
    category = column(data, "category_code")
    quantity = column(data, "quantity")
    price = column(data, "unit_price")
    cost = column(data, "unit_cost")
    discount = column(data, "discount_rate")
    stock = column(data, "stock_before_units")
    payment = column(data, "payment_code")
    rating = column(data, "customer_rating")

    known_product = np.isin(product, list(CATEGORY_OF_PRODUCT))
    expected = expected_category(product)

    return {
        "duplicate transaction_id": duplicate_id_mask(ids),
        "invalid transaction_id": ~is_whole(ids) | ~(ids > 0),
        "invalid day": ~is_whole(day) | ~((day >= 1) & (day <= 30)),
        "unknown outlet": ~np.isin(outlet, [1, 2, 3]),
        "unknown product": ~known_product,
        "unknown payment": ~np.isin(payment, [1, 2, 3, 4]),
        "category mismatch": known_product & (category != expected),
        "quantity not positive": quantity <= 0,
        "quantity not whole": np.isfinite(quantity) & ~is_whole(quantity),
        "price not positive": price <= 0,
        "negative unit cost": cost < 0,
        "discount outside 0-1": ~((discount >= 0) & (discount <= 1)),
        "negative stock": stock < 0,
        "invalid rating": np.isfinite(rating) & ~((rating >= 1) & (rating <= 5)),
        "infinite value": np.isinf(data).any(axis=1),
    }


def missing_masks(data):
    return {
        "missing unit_price": np.isnan(column(data, "unit_price")),
        "missing unit_cost": np.isnan(column(data, "unit_cost")),
        "missing customer_rating": np.isnan(column(data, "customer_rating")),
    }


def rule_counts(masks):
    table = np.vstack(list(masks.values()))
    return {
        "per_rule": {name: int(mask.sum()) for name, mask in masks.items()},
        "total_violations": int(table.sum()),
        "unique_rows_affected": int(table.any(axis=0).sum()),
    }