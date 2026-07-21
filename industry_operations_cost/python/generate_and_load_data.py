# Industry Operations & Cost Optimization - Data Generation & Cleaning
# Author: Juan Jose Carrascal Pinzon
#
# Generates a fake manufacturing plant: 6 production lines, a year of daily
# production logs (for OEE - Overall Equipment Effectiveness), and monthly
# cost breakdowns. Adds dirty data on purpose, cleans it with pandas. The
# clean CSVs feed the Excel analysis (no SQL in this project).
#
# Run: python generate_and_load_data.py

import random
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

N_LINES = 6
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)
PLANNED_MINUTES_PER_DAY = 8 * 60  # one 8-hour shift per line per day

THIS_PROJECT_DIR = Path(__file__).resolve().parent

RAW_DIR = THIS_PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = THIS_PROJECT_DIR / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

AREAS = ["Assembly", "Packaging", "Machining"]
DOWNTIME_REASONS = ["Changeover", "Mechanical Failure", "Material Shortage", "Planned Maintenance", "Operator Break"]
COST_TYPES = ["Labor", "Energy", "Maintenance", "Materials"]


def build_lines():
    rows = []
    for lid in range(1, N_LINES + 1):
        rows.append({
            "line_id": lid,
            "line_name": f"Line {lid}",
            "area": random.choice(AREAS),
            "target_units_per_hour": random.randint(80, 200),
        })
    return pd.DataFrame(rows)


def build_production_log(lines_df: pd.DataFrame):
    rows = []
    log_id = 1
    n_days = (END_DATE - START_DATE).days + 1
    for _, line in lines_df.iterrows():
        # each line has its own baseline reliability - some lines are just
        # older/less reliable than others, which is what makes comparing
        # lines in the analysis meaningful
        base_downtime_rate = np.random.uniform(0.03, 0.20)
        base_defect_rate = np.random.uniform(0.01, 0.06)

        for d in range(n_days):
            prod_date = START_DATE + timedelta(days=d)
            planned_minutes = PLANNED_MINUTES_PER_DAY

            downtime_minutes = int(np.random.exponential(base_downtime_rate * planned_minutes))
            downtime_minutes = min(downtime_minutes, planned_minutes)
            downtime_reason = random.choice(DOWNTIME_REASONS) if downtime_minutes > 0 else None

            operating_minutes = planned_minutes - downtime_minutes
            hourly_rate = line["target_units_per_hour"] * np.random.uniform(0.85, 1.05)
            units_produced = int((operating_minutes / 60) * hourly_rate)
            units_defective = int(units_produced * base_defect_rate * np.random.uniform(0.5, 1.5))

            # --- inject dirty data on purpose ---
            if downtime_minutes > 0 and random.random() < 0.08:
                downtime_reason = None  # should have a reason but doesn't
            if random.random() < 0.02:
                units_produced = -units_produced  # sign error
            if random.random() < 0.015:
                units_defective = units_produced + 50  # impossible: more defects than units made

            rows.append({
                "log_id": log_id,
                "line_id": line["line_id"],
                "production_date": prod_date.strftime("%Y-%m-%d"),
                "planned_minutes": planned_minutes,
                "downtime_minutes": downtime_minutes,
                "downtime_reason": downtime_reason,
                "units_produced": units_produced,
                "units_defective": units_defective,
            })
            log_id += 1

    df = pd.DataFrame(rows)
    dupes = df.sample(frac=0.01, random_state=SEED)
    df = pd.concat([df, dupes], ignore_index=True)
    return df


def build_monthly_costs(lines_df: pd.DataFrame):
    rows = []
    cost_id = 1
    months = pd.date_range(START_DATE, END_DATE, freq="MS")
    for _, line in lines_df.iterrows():
        for month in months:
            for cost_type in COST_TYPES:
                base = {"Labor": 18000, "Energy": 6000, "Maintenance": 4000, "Materials": 25000}[cost_type]
                amount = round(base * np.random.uniform(0.8, 1.3), 2)
                if random.random() < 0.02:
                    amount = None  # missing cost entry for the month
                rows.append({
                    "cost_id": cost_id,
                    "line_id": line["line_id"],
                    "cost_month": month.strftime("%Y-%m"),
                    "cost_type": cost_type,
                    "amount": amount,
                })
                cost_id += 1
    return pd.DataFrame(rows)


def clean_production_log(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="log_id", keep="first")

    df["units_produced"] = df["units_produced"].abs()

    # can't have more defective units than units produced - cap it, this is
    # a data entry error, not a real quality event this extreme
    df["units_defective"] = df[["units_produced", "units_defective"]].min(axis=1)
    df["units_defective"] = df["units_defective"].clip(lower=0)

    df["downtime_minutes"] = df["downtime_minutes"].clip(upper=df["planned_minutes"])
    df["downtime_reason"] = df["downtime_reason"].fillna("Unspecified")

    df["production_date"] = pd.to_datetime(df["production_date"], errors="coerce")
    df = df.dropna(subset=["production_date"])

    return df.reset_index(drop=True)


def clean_costs(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # a missing cost entry is a real gap (someone didn't log it), not zero
    # spend - leaving it null keeps SUM()/AVG() honest instead of hiding it
    return df.reset_index(drop=True)


def main():
    print("Generating plant operations data...")
    lines = build_lines()
    production_raw = build_production_log(lines)
    costs_raw = build_monthly_costs(lines)
    print(f"  lines: {len(lines)} | production logs: {len(production_raw)} | cost entries: {len(costs_raw)}")

    production_raw.to_csv(RAW_DIR / "production_log_raw.csv", index=False)
    costs_raw.to_csv(RAW_DIR / "monthly_costs_raw.csv", index=False)

    print("\nCleaning...")
    production_clean = clean_production_log(production_raw)
    costs_clean = clean_costs(costs_raw)
    print(f"  production logs: {len(production_raw)} -> {len(production_clean)} rows")

    lines.to_csv(PROCESSED_DIR / "lines_clean.csv", index=False)
    production_clean.to_csv(PROCESSED_DIR / "production_log_clean.csv", index=False)
    costs_clean.to_csv(PROCESSED_DIR / "monthly_costs_clean.csv", index=False)
    print(f"  saved clean csvs to {PROCESSED_DIR}")

    print("\nDone! Clean CSVs are ready in data/processed/ -")
    print("open Excel/industry_operations_cost/operations_analysis.xlsx for the analysis,")
    print("or re-import the 3 clean CSVs there if you regenerated the data.")


if __name__ == "__main__":
    main()
