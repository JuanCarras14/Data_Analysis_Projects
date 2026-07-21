# Wastewater Effluent Quality - Load & Clean
# Author: Juan Jose Carrascal Pinzon
#
# This one uses REAL data: the UCI "Water Treatment Plant" dataset (donated
# 1993, 527 daily records from an urban wastewater treatment plant). Source:
# https://archive.ics.uci.edu/dataset/106/water+treatment+plant
#
# Unlike the other projects in this repo, I didn't generate this data - I
# only renamed columns, added a date index, and loaded it into SQLite. The
# missing values here are the plant's real sensor gaps, not something I
# injected, so I handle them differently too (see notes below).
#
# Run: python load_and_clean.py

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd

THIS_PROJECT_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_PROJECT_DIR.parent.parent

RAW_PATH = THIS_PROJECT_DIR / "data" / "raw" / "water_treatment_raw.csv"
PROCESSED_DIR = THIS_PROJECT_DIR / "data" / "processed"
DB_PATH = REPO_ROOT / "SQL" / "wastewater_effluent_quality" / "database" / "wastewater.db"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# The plant treats water in 3 stages: primary settler -> biological reactor
# -> secondary settler. Sensors read the water at 4 points: as it enters the
# plant (E), before the primary settler (P), before the secondary settler
# (D), and as it leaves the plant (S) - the S columns are the effluent,
# which is what "calidad del efluente" (effluent quality) is about.
COLUMN_NAMES = {
    "class": "plant_status",
    # Influent (E) - raw water entering the plant
    "Q-E": "influent_flow_m3d",
    "ZN-E": "influent_zinc_mgl",
    "PH-E": "influent_ph",
    "DBO-E": "influent_bod_mgl",
    "DQO-E": "influent_cod_mgl",
    "SS-E": "influent_ss_mgl",
    "SSV-E": "influent_vss_pct",
    "SED-E": "influent_sediments_mll",
    "COND-E": "influent_conductivity_uscm",
    # Primary settler input (P)
    "PH-P": "primary_ph",
    "DBO-P": "primary_bod_mgl",
    "SS-P": "primary_ss_mgl",
    "SSV-P": "primary_vss_pct",
    "SED-P": "primary_sediments_mll",
    "COND-P": "primary_conductivity_uscm",
    # Secondary settler input (D) - after the biological reactor
    "PH-D": "secondary_ph",
    "DBO-D": "secondary_bod_mgl",
    "DQO-D": "secondary_cod_mgl",
    "SS-D": "secondary_ss_mgl",
    "SSV-D": "secondary_vss_pct",
    "SED-D": "secondary_sediments_mll",
    "COND-D": "secondary_conductivity_uscm",
    # Effluent (S) - the treated water leaving the plant, what gets discharged
    "PH-S": "effluent_ph",
    "DBO-S": "effluent_bod_mgl",
    "DQO-S": "effluent_cod_mgl",
    "SS-S": "effluent_ss_mgl",
    "SSV-S": "effluent_vss_pct",
    "SED-S": "effluent_sediments_mll",
    "COND-S": "effluent_conductivity_uscm",
    # Removal efficiency (RD = "rendimiento de depuracion", % removed at each stage)
    "RD-DBO-P": "removal_bod_primary_pct",
    "RD-SS-P": "removal_ss_primary_pct",
    "RD-SED-P": "removal_sed_primary_pct",
    "RD-DBO-S": "removal_bod_secondary_pct",
    "RD-DQO-S": "removal_cod_secondary_pct",
    "RD-DBO-G": "removal_bod_global_pct",
    "RD-DQO-G": "removal_cod_global_pct",
    "RD-SS-G": "removal_ss_global_pct",
    "RD-SED-G": "removal_sed_global_pct",
}

# Generic secondary-treatment discharge reference limits, used later for the
# compliance query. These are illustrative (typical BOD/COD/SS limits used
# in many discharge permits), not a specific country's actual regulation -
# noted in the SQL file and README too.
BOD_LIMIT_MGL = 40
COD_LIMIT_MGL = 160
SS_LIMIT_MGL = 60


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW_PATH)
    df = df.rename(columns=COLUMN_NAMES)
    return df


def add_date_index(df: pd.DataFrame) -> pd.DataFrame:
    """The original dataset has no calendar dates, just daily readings in
    order. I'm adding a day_id (the real, meaningful sequence) and a
    made-up sample_date so the data is easier to plot on a timeline - the
    sequence is real, the actual calendar dates are not."""
    df = df.copy()
    df.insert(0, "day_id", range(1, len(df) + 1))
    start_date = datetime(2023, 1, 1)
    df.insert(1, "sample_date", [
        (start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(len(df))
    ])
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Real exact-duplicate rows would still be worth removing if present
    df = df.drop_duplicates(subset=[c for c in df.columns if c not in ("day_id", "sample_date")])

    # All the sensor columns should be numeric - pandas already infers most
    # of these as floats because of the blanks, but this makes it explicit
    # and catches anything that slipped through as text.
    numeric_cols = [c for c in df.columns if c not in ("day_id", "sample_date", "plant_status")]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # pH has a hard physical range (0-14). Anything outside that is a
    # sensor/typing error, not a real reading - null it out rather than
    # guess a replacement.
    for ph_col in ["influent_ph", "primary_ph", "secondary_ph", "effluent_ph"]:
        out_of_range = ~df[ph_col].between(0, 14) & df[ph_col].notna()
        df.loc[out_of_range, ph_col] = pd.NA

    # NOTE on missing values: I'm deliberately NOT dropping rows or filling
    # gaps here. Almost every row is missing at least one of the 38 sensor
    # readings (real telemetry gaps), so dropna() would gut the dataset,
    # and filling a chemistry reading with a guessed number could hide a
    # real problem. NULLs stay as NULLs - SQL's AVG()/SUM() already skip
    # them correctly, which is the honest way to handle sensor gaps.

    return df.reset_index(drop=True)


def main():
    print("Loading real UCI wastewater treatment plant data...")
    raw = load_raw()
    print(f"  {len(raw)} rows, {len(raw.columns)} columns")

    missing_pct = (raw.isna().mean() * 100).round(1)
    worst = missing_pct.sort_values(ascending=False).head(5)
    print("  columns with the most missing values:")
    for col, pct in worst.items():
        print(f"    {col}: {pct}% missing")

    print("\nCleaning...")
    dated = add_date_index(raw)
    clean_df = clean(dated)
    print(f"  {len(clean_df)} rows after removing exact duplicates")

    clean_df.to_csv(PROCESSED_DIR / "water_treatment_clean.csv", index=False)
    print(f"  saved to {PROCESSED_DIR}")

    print("\nLoading into SQLite...")
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    try:
        clean_df.to_sql("plant_readings", conn, index=False, if_exists="replace")
        conn.commit()
    finally:
        conn.close()
    print(f"  database saved to {DB_PATH}")

    print("\nDone! Now go run the queries in SQL/wastewater_effluent_quality/analytics_queries.sql")


if __name__ == "__main__":
    main()
