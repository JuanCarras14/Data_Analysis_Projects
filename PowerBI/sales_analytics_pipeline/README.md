# Sales Analytics Pipeline - Power BI Dashboard

Star schema model + DAX measures on top of the SQLite database from the SQL part, to build a sales dashboard.

Other parts: [Python](../../Python/sales_analytics_pipeline) · [SQL](../../SQL/sales_analytics_pipeline)

## Connecting the data

Get Data -> ODBC/SQLite, pointing to `../../SQL/sales_analytics_pipeline/database/sales_warehouse.db`. If the SQLite driver isn't set up, import the CSVs from `../../Python/sales_analytics_pipeline/data/processed/` instead.

## Data model

```
customers (customer_id) ---< orders >--- products (product_id)
                              |
                          date table (order_date)
```

1. Import `customers`, `products`, `orders`.
2. Add a date table: `Date = CALENDAR(MIN(orders[order_date]), MAX(orders[order_date]))`.
3. Relationships: `customers[customer_id] -> orders[customer_id]`, `products[product_id] -> orders[product_id]`, `Date[Date] -> orders[order_date]`.
4. Mark `Date` as a date table.

## DAX measures

```dax
Total Revenue = SUM(orders[net_revenue])

Total Cost = SUMX(orders, orders[quantity] * RELATED(products[unit_cost]))

Total Profit = [Total Revenue] - [Total Cost]

Profit Margin % = DIVIDE([Total Profit], [Total Revenue])

Average Order Value = DIVIDE([Total Revenue], DISTINCTCOUNT(orders[order_id]))

Revenue Prior Year = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(Date[Date]))

Revenue YoY % = DIVIDE([Total Revenue] - [Revenue Prior Year], [Revenue Prior Year])

Revenue Prior Month = CALCULATE([Total Revenue], DATEADD(Date[Date], -1, MONTH))

Revenue MoM % = DIVIDE([Total Revenue] - [Revenue Prior Month], [Revenue Prior Month])
```

## Pages

- Overview: revenue, profit margin, YoY/MoM cards, monthly trend.
- Customers: top customers table, revenue by segment.
- Products: revenue and profit by category, top products.

## Project Status

🔴 Not started - model and measures planned above, dashboard build pending
