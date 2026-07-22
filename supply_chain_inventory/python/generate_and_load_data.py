# Supply Chain & Inventory Optimization - Data Generation & Cleaning
# Author: Juan Jose Carrascal Pinzon
#
# Generates fake products, suppliers, and a week-by-week inventory
# simulation (demand draws stock down, low stock triggers a purchase
# order, the order arrives late or on time depending on the supplier).
# Adds dirty data on purpose, cleans it, loads into SQLite.
#
# Run: python generate_and_load_data.py

import sqlite3
import random
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

N_PRODUCTS = 80
N_SUPPLIERS = 15
N_WEEKS = 52
START_DATE = datetime(2024, 1, 1)

THIS_PROJECT_DIR = Path(__file__).resolve().parent

RAW_DIR = THIS_PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = THIS_PROJECT_DIR / "data" / "processed"
DB_PATH = THIS_PROJECT_DIR.parent / "sql" / "database" / "supply_chain.db"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

CATEGORIES = ["Electronics", "Apparel", "Home Goods", "Food", "Tools"]
REGIONS = ["Domestic", "Asia", "Europe", "Latin America"]


def build_suppliers():
    rows = []
    for sid in range(1, N_SUPPLIERS + 1):
        rows.append({
            "supplier_id": sid,
            "supplier_name": f"Supplier {sid}",
            "region": random.choice(REGIONS),
            "nominal_lead_time_days": random.choice([7, 10, 14, 21, 30]),
            # higher = more likely to deliver on time; used to simulate
            # delays below, not saved to the table (not a directly observed column)
            "_reliability": np.random.uniform(0.5, 0.95),
        })
    return pd.DataFrame(rows)


def build_products(suppliers_df):
    rows = []
    for pid in range(1, N_PRODUCTS + 1):
        supplier = suppliers_df.sample(1, random_state=SEED + pid).iloc[0]
        avg_weekly_demand = max(1, int(np.random.exponential(15)))
        rows.append({
            "product_id": pid,
            "product_name": f"Product {pid:03d}",
            "category": random.choice(CATEGORIES),
            "supplier_id": supplier["supplier_id"],
            "unit_cost": round(np.random.uniform(3, 150), 2),
            "reorder_point": int(avg_weekly_demand * 2.5),   # ~2.5 weeks of demand
            "order_quantity": int(avg_weekly_demand * 6),    # order ~6 weeks of demand at a time
            "_avg_weekly_demand": avg_weekly_demand,
        })
    return pd.DataFrame(rows)


def simulate(products_df: pd.DataFrame, suppliers_df: pd.DataFrame):
    """Week-by-week per product: demand draws stock down, a low stock
    triggers a purchase order, the order arrives late or on time depending
    on the supplier's reliability. This has to be a loop, not vectorized -
    each week's stock level depends on the result of the previous week,
    so there's no way to compute all 52 weeks at once with column math."""
    suppliers_lookup = suppliers_df.set_index("supplier_id").to_dict("index")

    snapshot_rows = []
    po_rows = []
    po_id = 1

    for _, prod in products_df.iterrows():
        supplier = suppliers_lookup[prod["supplier_id"]]
        stock = prod["reorder_point"] * 2  # starting stock
        pending_po = None  # dict with arrival_week, quantity if an order is in transit

        for week in range(N_WEEKS):
            week_date = START_DATE + timedelta(weeks=week)

            # order arrives this week?
            if pending_po is not None and week >= pending_po["arrival_week"]:
                stock += pending_po["quantity"]
                po_rows.append(pending_po["po_record"])
                pending_po = None

            demand = max(0, int(np.random.normal(prod["_avg_weekly_demand"], prod["_avg_weekly_demand"] * 0.3)))
            stock -= demand
            stockout = stock < 0
            stock = max(0, stock)

            snapshot_rows.append({
                "product_id": prod["product_id"],
                "snapshot_date": week_date.strftime("%Y-%m-%d"),
                "stock_on_hand": stock,
                "stockout": int(stockout),
            })

            # low stock and nothing already on order -> place a purchase order
            if stock < prod["reorder_point"] and pending_po is None:
                lead_time_days = supplier["nominal_lead_time_days"]
                delay_days = 0 if random.random() < supplier["_reliability"] else random.randint(3, 14)
                arrival_week = week + max(1, round((lead_time_days + delay_days) / 7))
                order_date = week_date
                expected_delivery = order_date + timedelta(days=lead_time_days)
                actual_delivery = order_date + timedelta(days=lead_time_days + delay_days)

                pending_po = {
                    "arrival_week": arrival_week,
                    "quantity": prod["order_quantity"],
                    "po_record": {
                        "po_id": po_id,
                        "product_id": prod["product_id"],
                        "supplier_id": prod["supplier_id"],
                        "order_date": order_date.strftime("%Y-%m-%d"),
                        "expected_delivery_date": expected_delivery.strftime("%Y-%m-%d"),
                        "actual_delivery_date": actual_delivery.strftime("%Y-%m-%d"),
                        "quantity_ordered": prod["order_quantity"],
                    },
                }
                po_id += 1

    return pd.DataFrame(snapshot_rows), pd.DataFrame(po_rows)


def dirty_up(snapshots: pd.DataFrame, purchase_orders: pd.DataFrame):
    """Inject the usual data quality problems, after the simulation, so
    the simulation logic itself stays easy to follow."""
    snapshots = snapshots.copy()
    purchase_orders = purchase_orders.copy()

    # a few negative stock readings (sensor/count error, not a real state)
    bad_idx = snapshots.sample(frac=0.01, random_state=SEED).index
    snapshots.loc[bad_idx, "stock_on_hand"] = -snapshots.loc[bad_idx, "stock_on_hand"] - 1

    # some purchase orders missing a supplier_id, a few duplicated
    missing_idx = purchase_orders.sample(frac=0.02, random_state=SEED).index
    purchase_orders.loc[missing_idx, "supplier_id"] = None
    dupes = purchase_orders.sample(frac=0.015, random_state=SEED)
    purchase_orders = pd.concat([purchase_orders, dupes], ignore_index=True)

    return snapshots, purchase_orders


def clean_snapshots(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["stock_on_hand"] = df["stock_on_hand"].abs()  # fix negative readings
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"], errors="coerce")
    df = df.dropna(subset=["snapshot_date"])
    return df.reset_index(drop=True)


def clean_purchase_orders(df: pd.DataFrame, valid_supplier_ids: set) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="po_id", keep="first")

    # a PO with no known supplier can't be evaluated for on-time delivery -
    # keep the row but leave supplier_id null rather than drop the order
    # entirely, since the product/quantity/dates are still valid information
    df.loc[~df["supplier_id"].isin(valid_supplier_ids), "supplier_id"] = pd.NA

    for col in ["order_date", "expected_delivery_date", "actual_delivery_date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    return df.reset_index(drop=True)


def main():
    print("Simulating inventory (this takes a moment - it's a week-by-week loop)...")
    suppliers = build_suppliers()
    products = build_products(suppliers)
    snapshots_raw, po_raw = simulate(products, suppliers)
    snapshots_raw, po_raw = dirty_up(snapshots_raw, po_raw)
    print(f"  products: {len(products)} | suppliers: {len(suppliers)} | "
          f"snapshots: {len(snapshots_raw)} | purchase orders: {len(po_raw)}")

    products_out = products.drop(columns=["_avg_weekly_demand"])
    suppliers_out = suppliers.drop(columns=["_reliability"])

    products_out.to_csv(RAW_DIR / "products_raw.csv", index=False)
    suppliers_out.to_csv(RAW_DIR / "suppliers_raw.csv", index=False)
    snapshots_raw.to_csv(RAW_DIR / "inventory_snapshots_raw.csv", index=False)
    po_raw.to_csv(RAW_DIR / "purchase_orders_raw.csv", index=False)

    print("\nCleaning...")
    snapshots_clean = clean_snapshots(snapshots_raw)
    po_clean = clean_purchase_orders(po_raw, set(suppliers_out["supplier_id"]))
    print(f"  purchase orders: {len(po_raw)} -> {len(po_clean)} rows")

    products_out.to_csv(PROCESSED_DIR / "products_clean.csv", index=False)
    suppliers_out.to_csv(PROCESSED_DIR / "suppliers_clean.csv", index=False)
    snapshots_clean.to_csv(PROCESSED_DIR / "inventory_snapshots_clean.csv", index=False)
    po_clean.to_csv(PROCESSED_DIR / "purchase_orders_clean.csv", index=False)

    print("\nLoading into SQLite...")
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    try:
        products_out.to_sql("products", conn, index=False, if_exists="replace")
        suppliers_out.to_sql("suppliers", conn, index=False, if_exists="replace")
        snapshots_clean.to_sql("inventory_snapshots", conn, index=False, if_exists="replace")
        po_clean.to_sql("purchase_orders", conn, index=False, if_exists="replace")
        conn.commit()
    finally:
        conn.close()
    print(f"  database saved to {DB_PATH}")
    print("\nDone! Now go run the queries in ../sql/analytics_queries.sql")


if __name__ == "__main__":
    main()
