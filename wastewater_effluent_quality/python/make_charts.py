# Wastewater Effluent Quality - Charts
# Author: Juan Jose Carrascal Pinzon
#
# Two simple charts from the SQL analysis, so the findings in the README
# don't live in text alone. Reads straight from the SQLite database built
# by load_and_clean.py (run that first).
#
# Run: python make_charts.py

import sqlite3
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

THIS_PROJECT_DIR = Path(__file__).resolve().parent
DB_PATH = THIS_PROJECT_DIR.parent / "sql" / "database" / "wastewater.db"
IMAGES_DIR = THIS_PROJECT_DIR.parent / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

BOD_LIMIT_MGL = 40  # same reference limit used in the SQL compliance query


def load_readings() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql(
            "SELECT sample_date, effluent_bod_mgl, removal_bod_primary_pct, "
            "removal_bod_secondary_pct FROM plant_readings",
            conn,
        )
    finally:
        conn.close()
    df["sample_date"] = pd.to_datetime(df["sample_date"])
    return df


def chart_monthly_bod_trend(df: pd.DataFrame) -> None:
    """Monthly average effluent BOD vs. the reference discharge limit."""
    monthly = (
        df.dropna(subset=["effluent_bod_mgl"])
        .set_index("sample_date")["effluent_bod_mgl"]
        .resample("MS")
        .mean()
    )

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(monthly.index, monthly.values, marker="o", color="#1f4e79", label="Avg. effluent BOD")
    ax.axhline(BOD_LIMIT_MGL, color="#c0392b", linestyle="--", label=f"Reference limit ({BOD_LIMIT_MGL} mg/L)")
    ax.set_title("Effluent BOD by Month vs. Reference Discharge Limit")
    ax.set_ylabel("BOD (mg/L)")
    ax.set_xlabel("Month")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(IMAGES_DIR / "monthly_bod_trend.png", dpi=150)
    plt.close(fig)


def chart_removal_by_stage(df: pd.DataFrame) -> None:
    """Average BOD removal efficiency: primary settler vs. secondary (biological) stage."""
    primary_avg = df["removal_bod_primary_pct"].mean()
    secondary_avg = df["removal_bod_secondary_pct"].mean()

    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    bars = ax.bar(
        ["Primary settler", "Secondary (biological)"],
        [primary_avg, secondary_avg],
        color=["#7f9cbf", "#1f4e79"],
    )
    ax.bar_label(bars, fmt="%.1f%%", padding=3)
    ax.set_title("Average BOD Removal by Treatment Stage")
    ax.set_ylabel("BOD removed (%)")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(IMAGES_DIR / "removal_by_stage.png", dpi=150)
    plt.close(fig)


def main():
    print("Loading readings from the database...")
    df = load_readings()

    print("Building monthly BOD trend chart...")
    chart_monthly_bod_trend(df)

    print("Building removal-by-stage chart...")
    chart_removal_by_stage(df)

    print(f"\nDone! Charts saved to {IMAGES_DIR}")


if __name__ == "__main__":
    main()
