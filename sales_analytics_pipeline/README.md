# Sales & Customer Analytics Pipeline

An end-to-end pipeline on a synthetic sales dataset: generate it, clean it, then analyze it.

## How each tool is used

- **[Python](./python)** — generates ~500 customers, 60 products and ~6,000 orders, injects dirty data on purpose (missing values, duplicates, bad casing, negative quantities), and cleans it with pandas. The clean CSVs feed the Excel analysis.
- **[Excel](./excel)** — analyzes the clean data with formulas only (VLOOKUP, SUMIFS, COUNTIFS, LARGE, INDEX/MATCH): monthly revenue and growth, top customers, product performance, and segment/order-status breakdowns.

## What I found

- ~$7.28M total revenue from 5,133 completed orders.
- Revenue was basically flat between 2023 ($3.63M) and 2024 ($3.65M).
- Software is the top category by revenue (~$2.39M), ahead of Electronics (~$1.91M).
- ~12.6% of orders end up cancelled or returned.
