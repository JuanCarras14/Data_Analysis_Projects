# Sales Analytics Pipeline - Python

Generates a fake sales dataset (customers, products, orders), adds dirty data on purpose, cleans it with pandas, and loads it into SQLite for the SQL and Power BI parts.

Other parts: [SQL](../../SQL/sales_analytics_pipeline) · [Power BI](../../PowerBI/sales_analytics_pipeline)

## What it does

1. Generates ~500 customers, 60 products, ~6,000 orders.
2. Injects dirty data: missing values, duplicates, bad casing, negative quantities.
3. Saves the raw version to `data/raw/`.
4. Cleans it with pandas.
5. Saves the clean version to `data/processed/` and loads it into SQLite.

## Tools

- Python 3.10, pandas, numpy, sqlite3

## How to run

```bash
cd Python/sales_analytics_pipeline
pip install -r requirements.txt
python generate_and_load_data.py
```

## Project Status

🟢 Done
