# Customer Retention & Behavior - Data Generation & Cleaning
# Author: Juan Jose Carrascal Pinzon
#
# Generates fake customers + transactions with a realistic churn pattern
# baked in (so cohort retention actually declines over time, like a real
# business), adds dirty data on purpose, cleans it, and loads it into SQLite.
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

N_CUSTOMERS = 600
SIGNUP_WINDOW_MONTHS = 18   # customers sign up spread across this many months
DATASET_END = datetime(2024, 12, 31)  # "today" - no transactions after this

THIS_PROJECT_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_PROJECT_DIR.parent.parent

RAW_DIR = THIS_PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = THIS_PROJECT_DIR / "data" / "processed"
DB_PATH = REPO_ROOT / "SQL" / "customer_retention_behavior" / "database" / "customer_retention.db"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

CHANNELS = ["Organic Search", "Paid Ads", "Referral", "Social Media", "Email"]
REGIONS = ["North", "South", "East", "West", "Central"]
CATEGORIES = ["Subscription", "Add-on", "One-time Purchase"]

SIGNUP_START = DATASET_END - timedelta(days=30 * SIGNUP_WINDOW_MONTHS)


def month_start(dt: datetime) -> datetime:
    return dt.replace(day=1)


def add_months(dt: datetime, months: int) -> datetime:
    year = dt.year + (dt.month - 1 + months) // 12
    month = (dt.month - 1 + months) % 12 + 1
    return dt.replace(year=year, month=month, day=1)


def build_customers():
    rows = []
    for cid in range(1, N_CUSTOMERS + 1):
        signup_date = SIGNUP_START + timedelta(days=random.randint(0, 30 * SIGNUP_WINDOW_MONTHS))
        channel = random.choice(CHANNELS)
        if random.random() < 0.05:
            channel = None  # missing channel
        elif random.random() < 0.03:
            channel = channel.lower()  # inconsistent casing

        rows.append({
            "customer_id": cid,
            "signup_date": signup_date.strftime("%Y-%m-%d"),
            "acquisition_channel": channel,
            "region": random.choice(REGIONS),
            # each customer's own "stickiness" - used to simulate churn below,
            # not saved to the table (it's not a real observed attribute)
            "_retention_prob": np.random.uniform(0.55, 0.90),
        })
    return pd.DataFrame(rows)


def build_transactions(customers_df: pd.DataFrame):
    """For each customer, simulate month-by-month activity starting at
    signup. Each month they're still active, they might buy 1-3 times.
    Once they churn (stop being active), they don't come back - a simple
    'hard churn' model, which is enough to produce a realistic declining
    retention curve per signup cohort."""
    rows = []
    tid = 1
    for _, cust in customers_df.iterrows():
        signup = datetime.strptime(cust["signup_date"], "%Y-%m-%d")
        cohort_month = month_start(signup)
        retention_prob = cust["_retention_prob"]

        month_offset = 0
        active = True
        while active:
            current_month = add_months(cohort_month, month_offset)
            if current_month > DATASET_END:
                break

            # month 0 (signup month) always has at least one transaction
            if month_offset > 0:
                active = random.random() < retention_prob
                if not active:
                    break

            n_tx = random.randint(1, 3)
            for _ in range(n_tx):
                day_in_month = random.randint(0, 27)
                tx_date = current_month + timedelta(days=day_in_month)
                if tx_date > DATASET_END:
                    continue
                category = random.choices(CATEGORIES, weights=[0.6, 0.25, 0.15])[0]
                amount = round(np.random.uniform(15, 250), 2)

                cust_id = cust["customer_id"]
                if random.random() < 0.02:
                    cust_id = None  # orphaned transaction
                if random.random() < 0.015:
                    amount = -amount  # bad data: negative amount by mistake

                rows.append({
                    "transaction_id": tid,
                    "customer_id": cust_id,
                    "transaction_date": tx_date.strftime("%Y-%m-%d"),
                    "category": category,
                    "amount": amount,
                })
                tid += 1
            month_offset += 1

    df = pd.DataFrame(rows)
    # duplicate a few rows on purpose (double-charge / double-import scenario)
    dupes = df.sample(frac=0.01, random_state=SEED)
    df = pd.concat([df, dupes], ignore_index=True)
    return df


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=["_retention_prob"]).copy()
    df["acquisition_channel"] = df["acquisition_channel"].str.strip().str.title()
    df["acquisition_channel"] = df["acquisition_channel"].fillna("Unknown")
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")
    df = df.drop_duplicates(subset="customer_id", keep="first")
    return df.reset_index(drop=True)


def clean_transactions(df: pd.DataFrame, valid_customer_ids: set) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="transaction_id", keep="first")

    # can't attribute a transaction with no customer
    df = df.dropna(subset=["customer_id"])
    df["customer_id"] = df["customer_id"].astype(int)
    df = df[df["customer_id"].isin(valid_customer_ids)]

    # a negative "amount" here is a data error, not a real refund (this
    # dataset has no separate refund flag) - drop rather than guess
    df = df[df["amount"] > 0]

    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df = df.dropna(subset=["transaction_date"])

    return df.reset_index(drop=True)


def main():
    print("Generating customers and transactions (with simulated churn)...")
    customers_raw = build_customers()
    transactions_raw = build_transactions(customers_raw)

    customers_raw.drop(columns=["_retention_prob"]).to_csv(RAW_DIR / "customers_raw.csv", index=False)
    transactions_raw.to_csv(RAW_DIR / "transactions_raw.csv", index=False)
    print(f"  customers: {len(customers_raw)} | transactions: {len(transactions_raw)}")

    print("\nCleaning...")
    customers_clean = clean_customers(customers_raw)
    transactions_clean = clean_transactions(transactions_raw, set(customers_clean["customer_id"]))
    print(f"  customers: {len(customers_raw)} -> {len(customers_clean)} rows")
    print(f"  transactions: {len(transactions_raw)} -> {len(transactions_clean)} rows")

    customers_clean.to_csv(PROCESSED_DIR / "customers_clean.csv", index=False)
    transactions_clean.to_csv(PROCESSED_DIR / "transactions_clean.csv", index=False)

    print("\nLoading into SQLite...")
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    try:
        customers_clean.to_sql("customers", conn, index=False, if_exists="replace")
        transactions_clean.to_sql("transactions", conn, index=False, if_exists="replace")
        conn.commit()
    finally:
        conn.close()
    print(f"  database saved to {DB_PATH}")
    print("\nDone! Now go run the queries in SQL/customer_retention_behavior/analytics_queries.sql")


if __name__ == "__main__":
    main()
