# Sales Analytics Pipeline - Python

Generates a fake sales dataset (customers, products, orders), adds dirty data on purpose, and cleans it with pandas. The clean CSVs feed the Excel analysis.

Other parts: [Excel](../excel)

## What it does

1. Generates ~500 customers, 60 products, ~6,000 orders.
2. Injects dirty data: missing values, duplicates, bad casing, negative quantities.
3. Saves the raw version to `data/raw/`.
4. Cleans it with pandas.
5. Saves the clean version to `data/processed/`.

## Tools

- Python 3.10, pandas, numpy

## How to run

```bash
cd Python/sales_analytics_pipeline
pip install -r requirements.txt
python generate_and_load_data.py
```

## Project Status

🟢 Done
