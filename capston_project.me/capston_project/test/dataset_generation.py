import numpy as np
import pandas as pd

rng = np.random.default_rng(seed=42)
N = 5000

product_code = rng.integers(1, 9, size=N)
category_of_product = np.array([0, 1, 1, 1, 1, 2, 2, 3, 4])
base_price_of_product = np.array([0, 80, 90, 70, 60, 120, 130, 50, 40])

quantity = rng.integers(1, 6, size=N)
unit_price = np.round(base_price_of_product[product_code] * rng.uniform(0.95, 1.05, size=N), 2)

df = pd.DataFrame({
    "transaction_id": np.arange(1, N + 1),
    "day_index": rng.integers(1, 31, size=N),
    "outlet_id": rng.choice([1, 2, 3], size=N, p=[0.40, 0.35, 0.25]),
    "product_code": product_code,
    "category_code": category_of_product[product_code],
    "quantity": quantity,
    "unit_price": unit_price,
    "unit_cost": np.round(unit_price * rng.uniform(0.40, 0.65, size=N), 2),
    "discount_rate": rng.choice([0, 0.05, 0.10, 0.15, 0.20], size=N, p=[0.45, 0.20, 0.15, 0.12, 0.08]),
    "stock_before_units": quantity + rng.integers(1, 41, size=N),
    "payment_code": rng.integers(1, 5, size=N),
    "customer_rating": rng.integers(1, 6, size=N),
})



r = rng.choice(N, size=64, replace=False)

df.loc[r[0:4], "unit_price"] = np.nan
df.loc[r[4:8], "unit_cost"] = np.nan
df.loc[r[8:28], "customer_rating"] = np.nan

df.loc[r[29], "transaction_id"] = df.loc[r[28], "transaction_id"]
df.loc[r[31], "transaction_id"] = df.loc[r[30], "transaction_id"]
df.loc[r[32], "transaction_id"] = df.loc[r[30], "transaction_id"]

df.loc[r[33:37], "quantity"] = [0, 0, -1, -2]
df.loc[r[37:39], "unit_price"] = [-80, -50]
df.loc[r[39:41], "unit_cost"] = [-40, -25]
df.loc[r[41:43], "discount_rate"] = [1.5, 2.0]
df.loc[r[43:46], "customer_rating"] = [0, 6, 9]
df.loc[r[46:49], "category_code"] = df.loc[r[46:49], "category_code"] % 4 + 1
df.loc[r[49:51], "outlet_id"] = 9
df.loc[r[51:54], "unit_price"] = df.loc[r[51:54], "unit_price"] * 2
df.loc[r[54:59], "discount_rate"] = 0.9
df.loc[r[59:64], "stock_before_units"] = 0


print(df.shape)
print(df.isnull().sum())





