# Sales Analytics Pipeline - Data Generation & Cleaning
# Author: Juan Jose Carrascal Pinzon
#
# Builds a fake sales dataset (customers, products, orders), adds dirty
# data on purpose, cleans it with pandas, and loads it into SQLite.
#
# Run: python generate_and_load_data.py

import sqlite3
import random
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# Fixed seed so results are the same on every run.
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

N_CUSTOMERS = 500
N_PRODUCTS = 60
N_ORDERS = 6000

# Paths relative to this file, so it works from any clone.
THIS_PROJECT_DIR = Path(__file__).resolve().parent          # Python/sales_analytics_pipeline
REPO_ROOT = THIS_PROJECT_DIR.parent.parent                    # Data-Analysis-Projects

RAW_DIR = THIS_PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = THIS_PROJECT_DIR / "data" / "processed"
DB_PATH = REPO_ROOT / "SQL" / "sales_analytics_pipeline" / "database" / "sales_warehouse.db"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Reference lists used to build fake but realistic-looking records
# ---------------------------------------------------------------------------
FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
    "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Daniel",
    "Nancy", "Matthew", "Lisa", "Anthony", "Betty", "Mark", "Margaret",
    "Juan", "Camila", "Andres", "Valentina", "Carlos", "Sofia", "Luis",
    "Isabella", "Diego", "Mariana", "Miguel", "Laura",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson",
]
CITIES_STATES = [
    ("New York", "NY"), ("Los Angeles", "CA"), ("Chicago", "IL"),
    ("Houston", "TX"), ("Phoenix", "AZ"), ("Philadelphia", "PA"),
    ("San Antonio", "TX"), ("San Diego", "CA"), ("Dallas", "TX"),
    ("Austin", "TX"), ("Miami", "FL"), ("Atlanta", "GA"), ("Boston", "MA"),
    ("Seattle", "WA"), ("Denver", "CO"), ("Bogota", "DC"),
    ("Medellin", "ANT"), ("Toronto", "ON"), ("Mexico City", "CDMX"),
]
CUSTOMER_SEGMENTS = ["Consumer", "Corporate", "Small Business"]

PRODUCT_CATALOG = {
    "Electronics": ["Wireless Mouse", "Mechanical Keyboard", "USB-C Hub",
                    "27in Monitor", "Webcam HD", "Noise Cancelling Headset",
                    "Portable SSD 1TB", "Laptop Stand", "Bluetooth Speaker"],
    "Office Supplies": ["Ergonomic Chair", "Standing Desk", "Desk Lamp",
                         "Notebook Set", "Whiteboard", "Filing Cabinet",
                         "Stapler", "Printer Paper (Box)"],
    "Software": ["Analytics Suite License", "CRM Subscription (Annual)",
                 "Antivirus Bundle", "Cloud Storage Plan", "Project Mgmt Tool"],
    "Furniture": ["Bookshelf", "Conference Table", "Office Cabinet",
                  "Reception Sofa"],
}


def build_products():
    """Products table. Price is always above cost so margin makes sense."""
    rows = []
    product_id = 1
    for category, names in PRODUCT_CATALOG.items():
        for name in names * (N_PRODUCTS // len(PRODUCT_CATALOG) // len(names) + 1):
            unit_cost = round(np.random.uniform(5, 400), 2)
            margin_pct = np.random.uniform(0.20, 0.55)
            unit_price = round(unit_cost / (1 - margin_pct), 2)
            rows.append({
                "product_id": product_id,
                "product_name": name,
                "category": category,
                "unit_cost": unit_cost,
                "unit_price": unit_price,
            })
            product_id += 1
            if product_id > N_PRODUCTS:
                break
        if product_id > N_PRODUCTS:
            break
    return pd.DataFrame(rows)


def build_customers():
    """Customers table with dirty data on purpose: missing values,
    inconsistent casing, a few duplicated rows."""
    rows = []
    for cid in range(1, N_CUSTOMERS + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        city, state = random.choice(CITIES_STATES)
        signup_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 730))

        name = f"{first} {last}"
        if random.random() < 0.05:
            name = name.upper()            # inconsistent casing
        if random.random() < 0.05:
            name = f"  {name}  "           # extra whitespace

        email = f"{first.lower()}.{last.lower()}{cid}@example.com"
        if random.random() < 0.04:
            email = None                   # missing email
        elif random.random() < 0.03:
            email = email.replace("@", "")  # typo / malformed email

        segment = random.choice(CUSTOMER_SEGMENTS)
        if random.random() < 0.03:
            segment = None                 # missing segment

        rows.append({
            "customer_id": cid,
            "customer_name": name,
            "email": email,
            "city": city,
            "state": state,
            "segment": segment,
            "signup_date": signup_date.strftime("%Y-%m-%d"),
        })

    df = pd.DataFrame(rows)

    # duplicate a few rows on purpose, like a double-import would do
    dupes = df.sample(frac=0.02, random_state=SEED)
    df = pd.concat([df, dupes], ignore_index=True)
    return df


def build_orders(customers_df, products_df):
    """Orders table (fact table), with some bad rows: negative
    quantities, missing discount, missing customer id."""
    customer_ids = customers_df["customer_id"].unique().tolist()
    product_lookup = products_df.set_index("product_id")["unit_price"].to_dict()
    product_ids = list(product_lookup.keys())

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range_days = (end_date - start_date).days

    rows = []
    for oid in range(1, N_ORDERS + 1):
        cust_id = random.choice(customer_ids)
        prod_id = random.choice(product_ids)
        order_date = start_date + timedelta(days=random.randint(0, date_range_days))
        quantity = np.random.randint(1, 10)
        unit_price = product_lookup[prod_id]
        discount = round(random.choice([0, 0, 0, 0.05, 0.10, 0.15, 0.20]), 2)
        status = random.choices(
            ["Completed", "Cancelled", "Returned"], weights=[0.88, 0.06, 0.06]
        )[0]

        if random.random() < 0.02:
            quantity = -abs(quantity)      # someone typed a negative quantity
        if random.random() < 0.03:
            discount = None                # missing discount
        if random.random() < 0.02:
            cust_id = None                 # missing customer id

        rows.append({
            "order_id": oid,
            "customer_id": cust_id,
            "product_id": prod_id,
            "order_date": order_date.strftime("%Y-%m-%d"),
            "quantity": quantity,
            "unit_price": unit_price,
            "discount": discount,
            "order_status": status,
        })

    df = pd.DataFrame(rows)

    dupes = df.sample(frac=0.015, random_state=SEED)
    df = pd.concat([df, dupes], ignore_index=True)
    return df


# ---------------------------------------------------------------------------
# Cleaning functions
# ---------------------------------------------------------------------------
def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["customer_name"] = df["customer_name"].str.strip().str.title()
    df["email"] = df["email"].str.strip().str.lower()

    # if the email doesn't have an "@" it's not really an email, blank it out
    invalid_email_mask = df["email"].notna() & ~df["email"].str.contains("@", na=False)
    df.loc[invalid_email_mask, "email"] = np.nan

    df["segment"] = df["segment"].fillna("Unknown")
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")

    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="customer_id", keep="first")
    df = df.dropna(subset=["customer_name"])
    return df.reset_index(drop=True)


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["product_name"] = df["product_name"].str.strip()
    df = df.drop_duplicates(subset="product_id", keep="first")
    df = df[(df["unit_cost"] > 0) & (df["unit_price"] > 0)]
    return df.reset_index(drop=True)


def clean_orders(df: pd.DataFrame, valid_customer_ids: set, valid_product_ids: set) -> pd.DataFrame:
    df = df.copy()

    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="order_id", keep="first")

    # can't keep an order if we don't know who placed it
    df = df.dropna(subset=["customer_id"])
    df["customer_id"] = df["customer_id"].astype(int)
    df = df[df["customer_id"].isin(valid_customer_ids)]
    df = df[df["product_id"].isin(valid_product_ids)]

    df["quantity"] = df["quantity"].abs()          # fix negative quantities
    df["discount"] = df["discount"].fillna(0.0)    # assume no discount if missing

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df = df.dropna(subset=["order_date"])

    # revenue column I'll use later in SQL and Power BI
    df["net_revenue"] = (df["quantity"] * df["unit_price"] * (1 - df["discount"])).round(2)

    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Generating raw data (with some dirty data mixed in)...")
    products_raw = build_products()
    customers_raw = build_customers()
    orders_raw = build_orders(customers_raw, products_raw)

    products_raw.to_csv(RAW_DIR / "products_raw.csv", index=False)
    customers_raw.to_csv(RAW_DIR / "customers_raw.csv", index=False)
    orders_raw.to_csv(RAW_DIR / "orders_raw.csv", index=False)
    print(f"  customers: {len(customers_raw)} | products: {len(products_raw)} | orders: {len(orders_raw)}")
    print(f"  saved raw csvs to {RAW_DIR}")

    print("\nCleaning data with pandas...")
    products_clean = clean_products(products_raw)
    customers_clean = clean_customers(customers_raw)
    orders_clean = clean_orders(
        orders_raw,
        valid_customer_ids=set(customers_clean["customer_id"]),
        valid_product_ids=set(products_clean["product_id"]),
    )

    print(f"  customers: {len(customers_raw)} -> {len(customers_clean)} rows")
    print(f"  products:  {len(products_raw)} -> {len(products_clean)} rows")
    print(f"  orders:    {len(orders_raw)} -> {len(orders_clean)} rows")

    products_clean.to_csv(PROCESSED_DIR / "products_clean.csv", index=False)
    customers_clean.to_csv(PROCESSED_DIR / "customers_clean.csv", index=False)
    orders_clean.to_csv(PROCESSED_DIR / "orders_clean.csv", index=False)
    print(f"  saved clean csvs to {PROCESSED_DIR}")

    print("\nLoading clean tables into SQLite...")
    if DB_PATH.exists():
        DB_PATH.unlink()  # start fresh every time this runs

    conn = sqlite3.connect(DB_PATH)
    try:
        customers_clean.to_sql("customers", conn, index=False, if_exists="replace")
        products_clean.to_sql("products", conn, index=False, if_exists="replace")
        orders_clean.to_sql("orders", conn, index=False, if_exists="replace")
        conn.commit()
    finally:
        conn.close()

    print(f"  database saved to {DB_PATH}")
    print("\nDone! Now go run the queries in SQL/sales_analytics_pipeline/analytics_queries.sql")


if __name__ == "__main__":
    main()
