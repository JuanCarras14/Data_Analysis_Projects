# Industry Operations & Cost Optimization - Python

Generates a fake manufacturing plant: 6 production lines, a year of daily production logs, and monthly cost breakdowns. Adds dirty data on purpose, cleans it with pandas. The clean CSVs feed the Excel analysis.

Other parts: [Excel](../excel)

## What it does

1. Generates 6 lines, ~2,200 daily production log rows, 288 monthly cost entries.
2. Injects dirty data: missing downtime reasons, sign errors, impossible defect counts, duplicates.
3. Saves the raw version to `data/raw/`.
4. Cleans it with pandas (caps impossible values, fills/leaves nulls depending on the column).
5. Saves the clean version to `data/processed/`.

## Tools

- Python 3.10, pandas, numpy

## How to run

```bash
cd Python/industry_operations_cost
pip install -r requirements.txt
python generate_and_load_data.py
```

## Project Status

🟢 Done
