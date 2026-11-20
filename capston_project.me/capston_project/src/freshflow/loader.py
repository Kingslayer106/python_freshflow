from pathlib import Path

import numpy as np

EXPECTED_ROWS = 5000

COLUMNS = [
    "transaction_id", "day_index", "outlet_id", "product_code",
    "category_code", "quantity", "unit_price", "unit_cost",
    "discount_rate", "stock_before_units", "payment_code",
    "customer_rating",
]

COL = {name: index for index, name in enumerate(COLUMNS)}


def read_header(path):
    with open(path, "r") as file:
        return file.readline().strip().split(",")

def load_sales(path, expected_rows=EXPECTED_ROWS):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if read_header(path) != COLUMNS:
        raise ValueError("CSV header does not match the expected columns")

    with open(path, "r") as file:
        data = np.genfromtxt(file, delimiter=",", skip_header=1, ndmin=2)

    if expected_rows is not None:
        assert data.shape == (expected_rows, len(COLUMNS)), f"Unexpected shape: {data.shape}"
    return data

def save_array(path, data, columns=COLUMNS, fmt="%g"):
    with open(path, "w") as file:
        np.savetxt(file, data, delimiter=",", header=",".join(columns), comments="", fmt=fmt)