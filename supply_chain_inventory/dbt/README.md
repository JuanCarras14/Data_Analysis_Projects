# Supply Chain & Inventory - dbt

The transformation layer for this project, built with dbt on DuckDB. It takes the raw CSVs written by [the Python generator](../python) and turns them into tested, documented, modelled tables that the [SQL analysis](../sql) and the [Power BI report](../powerbi) read.

The cleaning logic used to live inside the pandas script. Moving it here makes it three things it was not before: **versioned**, **tested**, and **documented with its lineage**.

## Why DuckDB

No cloud account, no credentials, no warehouse to provision. `dbt build` creates a single `supply_chain.duckdb` file next to the project and reads the CSVs in place, so anyone who clones the repo can run the whole pipeline in about ten seconds.

## Layers

```text
sources (raw CSVs, defects intact)
    └── staging/   one model per source: typing, cleaning, explicit quality flags
            └── marts/   dimensions, facts and one analysis-ready scorecard
```

**Staging** is where the data is made trustworthy - one model per source table, no joins, no business logic.

**Marts** is where it is made useful - `dim_products`, `dim_suppliers`, `fct_inventory_weekly`, `fct_purchase_orders`, and `supplier_scorecard`.

## Data quality

The generator injects defects on purpose, so this pipeline has real problems to handle rather than hypothetical ones. Tests run at two levels and they do different jobs.

**On the sources**, tests run at `severity: warn`. They are not there to stop the pipeline - they are there to *measure* what arrives:

| What arrives broken | Rows |
| --- | --- |
| Negative stock readings | 42 |
| Purchase orders with no supplier | 19 |
| Duplicated `po_id` | 8 |

**On the models**, the same tests run at full severity and must pass. That contrast is the point: the warnings quantify the problem on the way in, the failures would catch a regression in the fix.

The three defects are handled differently on purpose:

- **Duplicated orders** are deduplicated on `po_id` with a window function, keeping the first occurrence.
- **Missing suppliers** are not dropped. The order is still valid information - product, quantity and dates are intact - so it is pointed at an explicit unknown member (`supplier_id = -1`) that carries a real name. The orders stay in the totals and the collection gap stays visible instead of disappearing. `supplier_scorecard` then excludes that member, because a supplier that was never recorded cannot be scored for delivery.
- **Negative stock readings** are discarded, not corrected. See below.

## A bug these tests found

The original pandas cleaning fixed negative readings with `abs()`. That looked right and was not: the defect the generator injects is `-value - 1`, so `abs()` leaves every corrected row one unit too high. On weeks that were genuinely stocked out, a true zero came back as one - which quietly contradicts the stockout flag those same rows carry.

`assert_stockout_implies_zero_stock` caught it. A week flagged as a stockout must end with no stock, and 5 rows did not.

The fix is not a better guess. An impossible reading tells us the value is wrong; it does not tell us what the value should have been. So the magnitude is discarded, the row is flagged with `was_invalid_reading`, and stock value simply excludes those weeks. It is the same call the [wastewater project](../../wastewater_effluent_quality) makes with missing sensor readings: the honest answer is "we do not know", not a plausible-looking invention.

Worth noting the asymmetry the test encodes: a stockout week always ends at zero, but a week can end at zero *without* a stockout, when demand happened to match stock exactly. Only the first direction is an invariant. Testing the reverse produced 67 false positives before I read the simulation closely enough to understand why.

## How to run

```bash
cd supply_chain_inventory/dbt
pip install dbt-duckdb
dbt deps
dbt build          # runs the models, then every test
dbt docs generate && dbt docs serve   # model docs and the lineage graph
```

`dbt build` should finish with 60 passing tests and 3 warnings - the three source warnings in the table above, which are expected.
