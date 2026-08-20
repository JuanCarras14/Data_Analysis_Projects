# Sales Analytics Pipeline - Power BI

Single-page sales overview built on the clean CSVs from [Python](../python). The heavier analysis in this project lives in the [Excel workbook](../excel); the dashboard is the summary layer on top of it.

## Tools

- Power BI Desktop
- Power Query
- DAX measures

## Data Model

A star schema: `orders` is the fact table, with `customers`, `products` and a generated `Date` table as dimensions, and all measures kept in a dedicated `_Measures` table rather than scattered across the fact table.

```DAX
Date = CALENDAR(MIN(orders[order_date]), MAX(orders[order_date]))
```

The Excel workbook is deliberately not a data source here. It computes the same figures from the same CSVs, so importing it would create two sources of truth for one number.

## The page

A year slicer, a KPI row (`Total Revenue`, `Total Profit`, `Profit Margin %`, `Average Order Value`), revenue by month across the full period, and revenue split by product category and by customer segment.

Every revenue measure counts completed orders only, so the dashboard reconciles exactly with the Excel workbook. Cancelled and returned orders are excluded from revenue rather than silently mixed into it - they are a quality problem, and the workbook measures them as one (~12.6% of all orders).

Revenue is essentially flat between 2023 ($3.63M) and 2024 ($3.65M), and the three customer segments land within a few percent of each other, so the interesting variation in this dataset is by category, not by segment.

## How to run

Open `sales_analytics_pipeline.pbix` in Power BI Desktop. The model ships with data cached, so it opens without a refresh; to rebuild it from source, regenerate the CSVs with the [Python script](../python) and point Power Query at `python/data/processed/`.
