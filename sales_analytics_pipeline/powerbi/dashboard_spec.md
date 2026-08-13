# Power BI Dashboard Spec - Sales Analytics Pipeline

## Data Sources

Import the clean CSVs from `sales_analytics_pipeline/python/data/processed/`:

- `customers_clean.csv` -> rename query to `customers`
- `products_clean.csv` -> rename query to `products`
- `orders_clean.csv` -> rename query to `orders`

Do not import `sales_analysis.xlsx`; the workbook computes the same analysis and would create two sources of truth.

## Power Query Checks

- `order_date`, `signup_date` -> Date
- `net_revenue`, `unit_price`, `unit_cost`, `discount` -> Decimal Number
- `_id` columns -> Whole Number

## Data Model

```text
customers (customer_id) ---< orders >--- products (product_id)
                              |
                          Date (order_date)
```

Date table:

```DAX
Date = CALENDAR(MIN(orders[order_date]), MAX(orders[order_date]))
Year = YEAR('Date'[Date])
Month = FORMAT('Date'[Date], "mmm")
Month Number = MONTH('Date'[Date])
Year-Month = FORMAT('Date'[Date], "yyyy-mm")
```

Relationships:

- `customers[customer_id]` 1:* `orders[customer_id]`
- `products[product_id]` 1:* `orders[product_id]`
- `Date[Date]` 1:* `orders[order_date]`

## Measures

Revenue uses completed orders only so it reconciles with the Excel workbook.

```DAX
Total Revenue =
CALCULATE(
    SUM(orders[net_revenue]),
    orders[order_status] = "Completed"
)

Total Cost =
CALCULATE(
    SUMX(orders, orders[quantity] * RELATED(products[unit_cost])),
    orders[order_status] = "Completed"
)

Total Profit = [Total Revenue] - [Total Cost]

Profit Margin % = DIVIDE([Total Profit], [Total Revenue])

Completed Orders =
CALCULATE(
    DISTINCTCOUNT(orders[order_id]),
    orders[order_status] = "Completed"
)

Average Order Value = DIVIDE([Total Revenue], [Completed Orders])

Total Orders = DISTINCTCOUNT(orders[order_id])

Lost Order % = DIVIDE([Total Orders] - [Completed Orders], [Total Orders])
```

Sanity check: `Total Revenue` should be about `$7.28M` from `5,133` completed orders.

## Pages

### Page 1 - Sales Overview

- Slicer: `Date[Year]`
- Cards: `Total Revenue`, `Total Profit`, `Profit Margin %`, `Average Order Value`
- Main chart: `Total Revenue` by `Date[Year-Month]`
- Detail left: `Total Revenue` by `products[category]`, sorted descending
- Detail right: `Total Revenue` by `customers[segment]`, sorted descending
- Finding: revenue is flat year over year

### Page 2 - Customers & Products

- Slicers: `products[category]`, `customers[segment]`
- Main left: top 10 customer table with `customer_name`, `segment`, `Total Revenue`, `Average Order Value`
- Main right: clustered bar with `Total Revenue` and `Total Profit` by `products[category]`
- Detail full width: product performance table with `product_name`, `category`, `Completed Orders`, `Total Revenue`, `Total Profit`, `Profit Margin %`
- Finding: category revenue leadership should be checked against profit after cost

### Page 3 - Order Quality

- Slicer: `Date[Year]`
- Cards: `Total Orders`, `Completed Orders`, `Lost Order %`
- Main left: donut of `orders[order_status]` by `Total Orders`
- Main right: `Lost Order %` by `Date[Year-Month]`
- Detail full width: `Lost Order %` by `products[category]`, sorted descending
- Finding: cancelled and returned orders are excluded from revenue but analyzed as lost orders

## Design System

- Canvas: 16:9, `1280 x 720`
- Page background: `#F4F6F8`
- Accent blue: `#1F4E79`
- Supporting grey: `#B9C3CF`
- Good: `#2B7A78`
- Bad: `#D4602E`
- Header title at `x=24`, `y=24`; slicer at `x=1016`, `y=24`
- KPI cards at `x=24`, `336`, `648`, `960`; `y=88`; `296 x 120`
- Main analysis row at `x=24`, `y=224`; detail row at `y=472`
- One written finding per page
- Single-accent rule: use blue for the main point, grey for context
