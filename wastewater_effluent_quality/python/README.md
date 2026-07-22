# Wastewater Effluent Quality - Python

Real dataset this time: the [UCI Water Treatment Plant dataset](https://archive.ics.uci.edu/dataset/106/water+treatment+plant) - 165 days of sensor readings from an actual urban wastewater treatment plant (influent, primary settler, secondary settler, and effluent quality).

Other parts: [SQL](../sql)

## What the script does

1. Loads the raw CSV and renames the original cryptic column codes (`DBO-S`, `RD-DQO-G`, etc.) into readable names (`effluent_bod_mgl`, `removal_cod_global_pct`...).
2. Adds a day index and a made-up calendar date (the daily sequence is real, the actual dates aren't - the original dataset doesn't have them).
3. Validates pH readings are physically possible (0-14), nulls out anything outside that range.
4. Loads the result into SQLite.

## Why this one is cleaned differently

Every other project in this repo either generates synthetic dirty data or works with a small, mostly-complete real dataset. This one is real sensor data with real gaps - almost every row is missing at least one of the 38 readings. Dropping incomplete rows would gut the dataset, and guessing values for a chemistry reading could hide a real plant problem. So here, missing values are left as `NULL` and reported, not dropped or filled.

## Tools

- Python 3.10, pandas, sqlite3

## How to run

```bash
cd wastewater_effluent_quality/python
pip install -r requirements.txt
python load_and_clean.py
```

## What I found

Once the cleaned data is in SQLite, the [SQL part](../sql) answers the actual questions. A few things that stood out:

- The plant met discharge limits on about 95% of the days (only ~5% went over at least one reference limit).
- The biological (secondary) stage does most of the work - around 83.6% average BOD removal, vs ~37.8% in the primary settler.
- Something I didn't expect: the days tagged as "overloaded" actually had the best average removal (90.8%). I'd want to look into that more before drawing conclusions.

## Project Status

🟢 Done
