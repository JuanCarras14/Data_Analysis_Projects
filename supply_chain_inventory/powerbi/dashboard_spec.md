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

### Unknown supplier member

Eleven purchase orders have no supplier on record. Power Query maps the null key to `-1`
and the supplier dimension carries a matching row:

```m
UnknownSupplierKey = Table.ReplaceValue(ChangedType, null, -1, Replacer.ReplaceValue, {"supplier_id"})
UnknownMember = Table.InsertRows(ChangedType, Table.RowCount(ChangedType),
    {[supplier_id = -1, supplier_name = "No supplier on record", region = "Unassigned", nominal_lead_time_days = null]})
```

Without it Power BI renders those orders under a nameless blank member, which reads as a
rendering artifact rather than the data-collection gap it actually is.

### Known limitation

`products` carries a `supplier_id` column with no relationship to `suppliers`. The only path
runs through `purchase_orders`, a fact table, which does not propagate filters onward, so
region cannot filter inventory or stockout measures. Inventory Health filters by category
instead. Resolving it means deciding which supplier relationship is authoritative, because a
direct `products` to `suppliers` link would make the path ambiguous.

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

Each page is laid out around its own question instead of reusing one template.

### Page 1 - Inventory Health

- Header: page title, `products[category]` slicer (dropdown) on the right
- Left rail, 280px wide: `Latest Inventory Value`, `Stockout Rate %`, `Products Stocked Out`, `On-Time %` stacked vertically
- Hero, 936x368: `Stockout Rate %` by `inventory_snapshots[snapshot_date]`, weekly
- Below: `Latest Inventory Value` by `products[category]`, and a category detail table
- Finding: stockout rate averages 8.6% but spikes above 20% three times before settling from July

The KPI rail is vertical so the 52-week timeline can take the full height. The page answers
what happened over the year, so time gets the space.

### Page 2 - Stockout Risk

- Header: page title, `products[category]` slicer (dropdown)
- Compact KPI strip, 88px tall: `Worst Product`, `Worst Product Stockout Rate %`, `Average Product Stockout Rate %`, `Stockout Weeks`
- Hero, 1232x488: table of products sorted by `Stockout Rate %` descending, carrying
  `Stockout Bar` (SVG bullet bar), `Stockout Weeks` and `Latest Stock On Hand`
- Finding: Product 027 is stocked out 17 of 52 weeks; several offenders cluster at exactly
  25.0% and 23.1%, the signature of a reorder point set too low against steady demand

No chart on this page. At 80 products a bar chart is unreadable, so the table is the visual.
`grid.imageHeight` must stay small (18px): Power BI reserves a tall default for image cells,
which collapses the row count and shrinks the bar to a hairline.

### Page 3 - Supplier Reliability

- Header: page title, `suppliers[region]` slicer (dropdown)
- Three cards, 400px each: `Supplier Count`, `On-Time %`, `Lowest On-Time Supplier`
- Hero, 816x472: `On-Time %` by `suppliers[supplier_name]`, sorted ascending so the worst reads first
- Right column, 400px: `Late Orders` card over a supplier detail table
- Finding: on-time rates run from 39.5% to over 90%, a spread a single average lead time would hide

Asymmetric two-column layout, deliberately unlike the other two pages.

## Design System

Canvas `1280 x 720`, page margin 24px, gutter 16px, header band 64px. Rows close exactly:

```text
y=24    header (title left, slicer right)   h=64
y=104   content                             h=592
        bottom margin 24
```

Widths: full `1232`, half `608`, quarter `296`. Slicer at `x=1032`, width `224`. The header
band is 64px rather than 48px because a dropdown slicer plus its label does not fit in 48.

| Role | Hex |
| --- | --- |
| Accent | `#1F4E79` |
| Good | `#2B7A78` |
| Bad | `#D4602E` |
| Neutral | `#B9C3CF` |
| Text | `#404040` |
| Page background | `#F4F6F8` |
| Card border | `#E6EAEF` |

Container styling lives in `IndustrialPremium.json`, shared with the other portfolio
dashboards, not in per-visual overrides.

### Stockout Bar

```DAX
Stockout Bar =
VAR Rate  = [Stockout Rate %]
VAR Scale = 0.35
VAR BarW  = 300
VAR W     = MAX(1, MIN(BarW, DIVIDE(Rate, Scale) * BarW))
VAR Fill  = IF(Rate >= 0.20, "#D4602E", IF(Rate >= 0.10, "#B9C3CF", "#2B7A78"))
RETURN
    "data:image/svg+xml;utf8," &
    "<svg xmlns='http://www.w3.org/2000/svg' width='" & BarW & "' height='18'>" &
    "<rect x='0' y='6' width='" & BarW & "' height='6' rx='3' fill='#E6EAEF'/>" &
    "<rect x='0' y='6' width='" & FORMAT(W, "0") & "' height='6' rx='3' fill='" & Fill & "'/>" &
    "</svg>"
```

The measure needs `dataCategory: ImageUrl`. The scale is a fixed 35% ceiling rather than the
row maximum, so bars stay comparable when the table is filtered.
