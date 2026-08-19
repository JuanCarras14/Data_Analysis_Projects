# Supply Chain & Inventory Optimization - Power BI

Three-page dashboard built from the SQLite tables in [SQL](../sql) and the clean CSVs in [Python](../python). It shares the portfolio palette and grid with the other dashboards, but each page is laid out around the question it answers rather than reusing one template.

## Tools

- Power BI Desktop
- Power Query
- DAX measures

## Pages

**Inventory Health**

![Inventory Health](../images/inventory_health.png)

KPIs run down a vertical rail on the left so the 52-week stockout timeline gets the full height of the page. The question here is what happened over the year, so time gets the space. Below it, inventory value by category and a category-level detail table.

Stockout rate averages 8.6% across the year, but the timeline shows it is not steady: it spikes above 20% three times before settling into a tighter band from July onward.

**Stockout Risk**

![Stockout Risk](../images/stockout_risk.png)

No chart on this page. With 80 products, a bar chart is unreadable, so the ranked table is the visual: each row carries an inline bullet bar drawn by a DAX measure that returns SVG, scaled against a fixed 35% ceiling so bars stay comparable between rows and coloured by risk band.

Product 027 tops the list at 32.7% - stocked out 17 of 52 weeks. The pattern worth noting is that several of the worst offenders sit at exactly 25.0% and 23.1%, which is what a reorder point set too low looks like when demand is steady.

**Supplier Reliability**

![Supplier Reliability](../images/supplier_reliability.png)

Asymmetric layout: a tall comparison of on-time delivery across suppliers on the left, sorted worst first, with late-order volume and a supplier table on the right.

On-time rates run from 39.5% to over 90%. A single "average lead time" number would hide that spread completely, which is the point of ranking suppliers individually.

## Design

Canvas is `1280 x 720`, 24px page margin, 16px gutters, and a 64px header band on every page. Rows close exactly on the canvas.

| Role | Hex |
| --- | --- |
| Accent | `#1F4E79` |
| Good | `#2B7A78` |
| Bad | `#D4602E` |
| Neutral | `#B9C3CF` |
| Page background | `#F4F6F8` |
| Card border | `#E6EAEF` |

Container styling lives in the report theme (`SupplyChainInventory.Report/StaticResources/RegisteredResources/IndustrialPremium.json`) rather than on individual visuals, so the report re-themes from one file.

## Data Quality

Eleven purchase orders arrived with no supplier on record. Rather than dropping them or letting Power BI render them as a nameless blank, the model assigns them to an explicit unknown member: Power Query maps the null key to `-1` and the supplier dimension carries a matching row named "No supplier on record". The orders stay in the totals and the gap stays visible instead of quietly disappearing.

## Power BI Build Notes

The editable Power BI project is in [supply_chain_inventory_pbip](./supply_chain_inventory_pbip):

- `SupplyChainInventory.pbip` opens the report in Power BI Desktop.
- `SupplyChainInventory.Report/` contains the PBIR report pages, visuals and theme.
- `SupplyChainInventory.SemanticModel/` contains the local TMDL semantic model, CSV imports, relationships and measures.

The PBIP folder is the source of truth. `supply_chain_inventory.pbix` is exported from it for anyone who wants a single downloadable file.

The model, DAX, page map and design rules are documented in [dashboard_spec.md](./dashboard_spec.md).

## Known Limitation

`products` has a `supplier_id` column but no relationship to `suppliers`; the only path runs through `purchase_orders`, which is a fact table and does not propagate filters onward. Region therefore cannot filter inventory or stockout measures, which is why Inventory Health filters by category instead. Resolving it means choosing which supplier relationship is authoritative, since a direct `products` to `suppliers` link would make the path ambiguous.

## How to run

Open `supply_chain_inventory/powerbi/supply_chain_inventory_pbip/SupplyChainInventory.pbip` in Power BI Desktop, then refresh. A PBIP stores model metadata only, so the tables are empty until the first refresh reads the CSVs.

## Project Status

Done
