# Power BI Dashboard Spec - Supply Chain & Inventory Optimization

## Data Source

Use the SQLite database at `supply_chain_inventory/sql/database/supply_chain.db`.

Import these tables:

- `products`
- `suppliers`
- `inventory_snapshots`
- `purchase_orders`

## Data Model

```text
suppliers (supplier_id) ---< products (product_id) ---< inventory_snapshots
     |
     ---< purchase_orders >--- products
```

Relationships:

- `products[product_id]` 1:* `inventory_snapshots[product_id]`
- `products[product_id]` 1:* `purchase_orders[product_id]`
- `suppliers[supplier_id]` 1:* `purchase_orders[supplier_id]`

`inventory_snapshots` and `purchase_orders` are separate fact tables at different grains, so they should not connect directly.

## Measures

```DAX
Total Stock On Hand = SUM(inventory_snapshots[stock_on_hand])

Inventory Value =
SUMX(
    inventory_snapshots,
    inventory_snapshots[stock_on_hand] * RELATED(products[unit_cost])
)

Latest Snapshot Date = MAX(inventory_snapshots[snapshot_date])

Latest Stock On Hand =
VAR LatestDate = [Latest Snapshot Date]
RETURN CALCULATE([Total Stock On Hand], inventory_snapshots[snapshot_date] = LatestDate)

Latest Inventory Value =
VAR LatestDate = [Latest Snapshot Date]
RETURN CALCULATE([Inventory Value], inventory_snapshots[snapshot_date] = LatestDate)

Stockout Weeks = SUM(inventory_snapshots[stockout])

Stockout Rate % = DIVIDE([Stockout Weeks], COUNTROWS(inventory_snapshots))

Products Stocked Out =
COUNTROWS(FILTER(VALUES(products[product_name]), CALCULATE(MAX(inventory_snapshots[stockout])) = 1))

Worst Product =
CONCATENATEX(TOPN(1, VALUES(products[product_name]), [Stockout Rate %], DESC), products[product_name], ", ")

Worst Product Stockout Rate % =
MAXX(TOPN(1, VALUES(products[product_name]), [Stockout Rate %], DESC), [Stockout Rate %])

Average Product Stockout Rate % =
AVERAGEX(VALUES(products[product_name]), [Stockout Rate %])

Total Orders = COUNTROWS(purchase_orders)

On-Time Orders =
CALCULATE(
    COUNTROWS(purchase_orders),
    purchase_orders[actual_delivery_date] <= purchase_orders[expected_delivery_date]
)

On-Time % = DIVIDE([On-Time Orders], [Total Orders])

Late Orders = [Total Orders] - [On-Time Orders]

Supplier Count = DISTINCTCOUNT(suppliers[supplier_id])

Lowest On-Time Supplier =
CONCATENATEX(TOPN(1, VALUES(suppliers[supplier_name]), [On-Time %], ASC), suppliers[supplier_name], ", ")
```

Note: `Inventory Value` should be filtered to the latest snapshot week before using it as a current inventory KPI; otherwise historical weekly snapshots are counted together.

## Pages

### Page 1 - Inventory Overview

- Slicer: `suppliers[region]`
- Cards: `Latest Inventory Value`, `Stockout Rate %`, `On-Time %`, `Products Stocked Out`
- Main chart: `Stockout Rate %` by snapshot week
- Detail left: latest-week `Inventory Value` by `products[category]`
- Detail right: `Total Orders` by `suppliers[region]`
- Finding: inventory value is filtered to the latest week to avoid double-counting snapshots

### Page 2 - Stockouts

- Slicer: `products[category]`
- Cards: `Worst Product`, `Worst Product Stockout Rate %`, `Average Product Stockout Rate %`, `Stockout Weeks`
- Main chart: top 15 `products[product_name]` by `Stockout Rate %`, sorted descending
- Detail table: `product_id`, `product_name`, `category`, `Stockout Rate %`
- Finding: Product 027 was stocked out 32.7% of tracked weeks

### Page 3 - Suppliers

- Slicer: `suppliers[region]`
- Cards: `Supplier Count`, `On-Time %`, `Lowest On-Time Supplier`, `Late Orders`
- Main chart: `On-Time %` by `suppliers[supplier_name]`, sorted ascending
- Detail table: `supplier_name`, `region`, `Total Orders`, `On-Time %`
- Finding: Supplier 7 has the lowest on-time rate, so average lead time alone hides reliability risk

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
