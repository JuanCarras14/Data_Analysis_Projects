# Industry Operations & Cost Optimization - Python

Generates a fake manufacturing plant: 6 production lines, a year of daily production logs, and monthly cost breakdowns (labor, energy, maintenance, materials). Each line has its own baseline reliability, so some lines are realistically worse than others - not everything is the same by design.

Other parts: [SQL](../../SQL/industry_operations_cost) · [Power BI](../../PowerBI/industry_operations_cost)

## What it does

1. Generates 6 lines with a target output rate, then a daily production log per line for a full year (planned time, downtime, downtime reason, units produced, defective units).
2. Generates monthly cost entries per line across 4 cost categories.
3. Injects dirty data: missing downtime reasons, sign errors, impossible defect counts (more defects than units made), missing cost entries, duplicate rows.
4. Cleans it and loads `lines`, `production_log`, `monthly_costs` into SQLite.

## Tools

- Python 3.10, pandas, numpy, sqlite3

## How to run

```bash
cd Python/industry_operations_cost
pip install -r requirements.txt
python generate_and_load_data.py
```

## Project Status

🟢 Done
