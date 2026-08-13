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

Stockout Weeks = SUM(inventory_snapshots[stockout])

Stockout Rate % = DIVIDE([Stockout Weeks], COUNTROWS(inventory_snapshots))

Total Orders = COUNTROWS(purchase_orders)

On-Time Orders =
CALCULATE(
    COUNTROWS(purchase_orders),
    purchase_orders[actual_delivery_date] <= purchase_orders[expected_delivery_date]
)

On-Time % = DIVIDE([On-Time Orders], [Total Orders])
```

Note: `Inventory Value` should be filtered to the latest snapshot week before using it as a current inventory KPI; otherwise historical weekly snapshots are counted together.

## Pages

### Page 1 - Inventory Overview

- Slicer: `suppliers[region]`
- Cards: latest-week `Inventory Value`, `Stockout Rate %`, `On-Time %`
- Main chart: `Stockout Rate %` by snapshot week
- Detail left: latest-week `Inventory Value` by `products[category]`
- Detail right: `Total Orders` by `suppliers[region]`
- Finding: inventory value is filtered to the latest week to avoid double-counting snapshots

### Page 2 - Stockouts

- Slicer: `products[category]`
- Cards: worst product, worst product stockout rate, average product stockout rate
- Main chart: top 15 `products[product_name]` by `Stockout Rate %`, sorted descending
- Detail table: `product_id`, `product_name`, `category`, `Stockout Rate %`
- Finding: Product 027 was stocked out 32.7% of tracked weeks

### Page 3 - Suppliers

- Slicer: `suppliers[region]`
- Cards: supplier count, `On-Time %`, lowest on-time supplier
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
