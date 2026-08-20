# Industry Operations & Cost Optimization - Power BI

Three-page dashboard built from the clean CSVs in [Python](../python). All three pages share one layout grid and one theme, so the report reads as a single artifact rather than three separate reports.

## Tools

- Power BI Desktop
- Power Query
- DAX measures

## Pages

**Overview**

![Overview](../images/overview.png)

The KPI row shows OEE next to all three of its factors - Availability, Performance and Quality - so the headline number decomposes on the page instead of standing alone. Below it, monthly downtime over the year, OEE by line against the 85% target, and a detail table with the gap, downtime rate and defect rate per line.

Average OEE is 81.2%, which is 3.8 points under target. Four of the six lines miss it, and the bar colour marks which ones.

**OEE Breakdown**

![OEE Breakdown](../images/oee_breakdown.png)

Diagnostic view of the worst-performing line. The cards break its OEE into the same three factors, so the cause is visible without opening a table.

Line 3 sits at 73.4% OEE. Its performance (94.6%) and quality (97.1%) are close to the plant average, but availability is 79.8% - the line is losing operating time, not running slow or scrapping units. The downtime ranking on the right points at where that time goes: operator breaks and changeovers together lose more minutes than mechanical failures.

The worst-line cards are driven by `TOPN` rather than hardcoded to Line 3, so the page stays correct if the data changes.

**Cost Analysis**

![Cost Analysis](../images/cost_analysis.png)

Total cost, cost per unit, materials share and the largest cost category, over cost by type, monthly cost split by type, and cost per unit through the year. Materials are 47% of spend, well ahead of labor, so any cost conversation starts there.

## Design

Canvas is `1280 x 720` with a 24px page margin and 16px gutters. Four rows - header, KPIs, charts, detail table - close exactly on the canvas, and the same grid repeats on every page.

| Role | Hex |
| --- | --- |
| Accent | `#1F4E79` |
| Good | `#2B7A78` |
| Bad | `#D4602E` |
| Neutral | `#B9C3CF` |
| Text | `#404040` |
| Page background | `#F4F6F8` |
| Card border | `#E6EAEF` |

White cards with a light border, 8px corners and a soft shadow sit on a grey page background. Container styling lives in the report theme rather than on individual visuals, so the report re-themes from one file: `IndustryOperationsCost.Report/StaticResources/RegisteredResources/IndustrialPremium.json`.

Colour is used to direct attention, not to decorate. Bars are a single accent blue except on OEE by Line, where the measure `OEE Bar Color` turns a bar orange when that line is below the 85% target.

## Data Model

Two fact tables at different grains - `production_log` is daily, `monthly_costs` is monthly - joined only through the shared `lines` dimension, never to each other:

- `lines[line_id]` 1:* `production_log[line_id]`
- `lines[line_id]` 1:* `monthly_costs[line_id]`

Monthly downtime is grouped by `production_log[production_month]`, a column added in Power Query rather than a DAX calculated column. A calculated column there closes the dependency graph through `monthly_costs[Cost per Unit]`, which resolves to `[Total Units]`, and refresh fails with a cyclic reference.

## Measures

OEE is a product of three factors, so the model keeps them as separate measures and multiplies them rather than computing one opaque number. `Theoretical Units` is the one that carries the real logic - it converts each day's actual running time into the units that line *should* have made at its rated speed:

```DAX
Theoretical Units =
SUMX(
    production_log,
    DIVIDE(production_log[planned_minutes] - production_log[downtime_minutes], 60)
        * RELATED(lines[target_units_per_hour])
)

Performance % = DIVIDE([Total Units], [Theoretical Units])

OEE % = [Availability %] * [Performance %] * [Quality %]
```

The diagnostic page resolves its subject at query time instead of naming a line, so the page stays correct if the data changes:

```DAX
Worst OEE Line =
CONCATENATEX(TOPN(1, VALUES(lines[line_name]), [OEE %], ASC), lines[line_name], ", ")

Worst Line Availability = CALCULATE([Availability %], TOPN(1, VALUES(lines[line_name]), [OEE %], ASC))
```

Conditional colour is measure-driven rather than a static rule, so the 85% target is defined once and both the chart and the KPI text read from it:

```DAX
OEE Bar Color = IF([OEE %] < [OEE Target], "#D4602E", "#1F4E79")
```

## Project files

- `IndustryOperationsCost.pbip` opens the report in Power BI Desktop.
- `IndustryOperationsCost.Report/` holds the PBIR pages, visuals and theme.
- `IndustryOperationsCost.SemanticModel/` holds the TMDL model: table definitions, relationships and measures.

The PBIP folder is the source of truth; `industry_operations_cost.pbix` is exported from it as a single downloadable file.

## How to run

Open `industry_operations_cost_pbip/IndustryOperationsCost.pbip` in Power BI Desktop. Set the `DataFolder` parameter to the absolute path of `industry_operations_cost/python/data/processed/` in your clone, then refresh: a PBIP stores model metadata only, so the tables are empty until the first refresh reads the CSVs.
