# Supply Chain & Inventory Optimization - Power BI

Dashboard design built from the SQLite database used by the [SQL analysis](../sql), using the same portfolio design system as the Wastewater Effluent Quality dashboard: header band, single blue accent, neutral supporting visuals, KPI cards at the top, and one written finding per page.

## Tools

- Power BI Desktop
- SQLite / ODBC import
- DAX measures

## Pages

**Inventory Overview**

![Inventory Overview](../images/overview.png)

Inventory value, stockout rate, and on-time order KPIs, plus stockout trend, latest inventory value by category, and purchase-order volume by supplier region.

**Stockouts**

![Stockouts](../images/stockouts.png)

Worst products by stockout rate plus a detail table for exact values. Product 027 is the highest-risk SKU.

**Suppliers**

![Suppliers](../images/suppliers.png)

Supplier on-time delivery chart and detail table. The page is sorted worst first so unreliable suppliers are visible immediately.

## Power BI Build Notes

The model, DAX, page map, and formatting rules are documented in [dashboard_spec.md](./dashboard_spec.md).

## How to run

Open Power BI Desktop, import the four SQLite tables from `supply_chain_inventory/sql/database/supply_chain.db`, apply the relationships and measures in [dashboard_spec.md](./dashboard_spec.md), and save the report as `supply_chain_inventory.pbix`.

## Project Status

Done
