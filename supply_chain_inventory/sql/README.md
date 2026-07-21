# Supply Chain & Inventory Optimization - SQL Analysis

Stockout and supplier performance analysis on top of the database from [Python/supply_chain_inventory](../python).

Other parts: [Python](../python)

## Tools

- SQLite
- DB Browser for SQLite
- Git / GitHub

## Queries (`analytics_queries.sql`)

1. Stockout rate by product, worst first.
2. Supplier on-time delivery performance.
3. Current inventory value by category (CTE).
4. Extra: purchase orders with no supplier on record (data quality check).

## Findings

- Worst product (Product 027) was stocked out 32.7% of the tracked weeks - a reorder point/quantity that's clearly too low for its demand.
- Supplier on-time rates range from 39.5% to over 90% - "average lead time" alone hides which suppliers are actually unreliable.
- Food and Electronics hold the most inventory value, despite Home Goods having more products - fewer, pricier items outweigh more, cheaper ones.
- 11 purchase orders have no supplier on record and can't be scored for on-time delivery - a real data collection gap, not something to quietly drop.

## How to run

```bash
cd SQL/supply_chain_inventory
sqlite3 database/supply_chain.db < analytics_queries.sql
```

## Project Status

🟢 Done
