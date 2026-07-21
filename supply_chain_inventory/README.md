# Supply Chain & Inventory Optimization

A week-by-week inventory simulation, then stockout and supplier performance analysis.

## How each tool is used

- **[Python](./python)** - builds 80 products and 15 suppliers and runs a 52-week simulation where demand draws down stock, low stock triggers a purchase order, and orders arrive on time or late based on supplier reliability. Injects dirty data, cleans it, and loads four tables into SQLite.
- **[SQL](./sql)** - stockout rate by product, supplier on-time delivery performance, inventory value by category (CTE), and a data-quality check for purchase orders with no supplier.

## What I found

- The worst product was stocked out 32.7% of the tracked weeks - its reorder point is clearly too low for its demand.
- Supplier on-time rates range from 39.5% to over 90% - "average lead time" alone hides which suppliers are actually unreliable.
- 11 purchase orders have no supplier on record - a real data-collection gap, not something to quietly drop.
