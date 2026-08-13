# Sales Analytics Pipeline - Power BI

Dashboard built on top of the clean CSVs from [Python](../python), using the same portfolio design system as the Wastewater Effluent Quality dashboard: header band, single blue accent, neutral supporting visuals, KPI cards at the top, and one written finding per page.

## Tools

- Power BI Desktop
- Power Query
- DAX measures

## Pages

**Sales Overview**

![Sales Overview](../images/overview.png)

KPI cards for completed-order revenue, profit, margin, and average order value. The page shows revenue by month, category, and segment. Revenue is basically flat between 2023 and 2024.

**Customers & Products**

![Customers & Products](../images/customers_products.png)

Top customer table, revenue vs profit by category, and product-level performance. This page checks whether the revenue leaders also hold up after product cost.

**Order Quality**

![Order Quality](../images/order_quality.png)

Order-status breakdown, lost-order trend, and lost-order rate by category. Cancelled and returned orders are not counted as revenue, but they are analyzed as their own quality issue.

## Power BI Build Notes

The model, DAX, page map, and formatting rules are documented in [dashboard_spec.md](./dashboard_spec.md).

## How to run

Open `sales_analytics_pipeline.pbix` in Power BI Desktop. If rebuilding from source, import the clean CSVs from `sales_analytics_pipeline/python/data/processed/`, apply the relationships and measures in [dashboard_spec.md](./dashboard_spec.md), and save the report in this folder.

## Project Status

Done
