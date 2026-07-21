# Supply Chain & Inventory Optimization - Python

Generates 80 products, 15 suppliers, and a week-by-week (52 weeks) inventory simulation: demand draws stock down, low stock triggers a purchase order, and the order arrives on time or late depending on the supplier. Adds dirty data on purpose, cleans it, loads into SQLite.

Other parts: [SQL](../sql)

## What it does

1. Builds products (category, unit cost, reorder point) and suppliers (region, lead time, reliability).
2. Simulates 52 weeks per product: demand reduces stock, stock below the reorder point triggers a purchase order, the order arrives late or on time based on the supplier's reliability.
3. Injects dirty data: a few negative stock readings, purchase orders missing a supplier, duplicate orders.
4. Cleans it and loads `products`, `suppliers`, `inventory_snapshots`, `purchase_orders` into SQLite.

## Why this one uses a loop instead of vectorized pandas

Every week's stock level depends on last week's stock level plus this week's demand and any order that arrived - that's a genuinely sequential process, not something `df["a"] * df["b"]`-style column math can express. See `learning-notes/python_guide_supply_chain_inventory.md` for why a loop is the right call here and not the performance trap flagged elsewhere in this repo.

## Tools

- Python 3.10, pandas, numpy, sqlite3

## How to run

```bash
cd Python/supply_chain_inventory
pip install -r requirements.txt
python generate_and_load_data.py
```

## Project Status

🟢 Done
