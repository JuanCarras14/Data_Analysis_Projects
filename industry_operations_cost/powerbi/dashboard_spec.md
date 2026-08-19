# Power BI Dashboard Spec - Industry Operations & Cost Optimization

## Data Sources

Import the clean CSVs from `industry_operations_cost/python/data/processed/`:

- `lines_clean.csv` -> rename query to `lines`
- `production_log_clean.csv` -> rename query to `production_log`
- `monthly_costs_clean.csv` -> rename query to `monthly_costs`

Do not import `operations_analysis.xlsx`; the workbook computes the same analysis and would create two sources of truth.

## Power Query Checks

- `production_date` -> Date
- `cost_month` -> Text in `yyyy-mm` format
- `amount` -> Decimal Number
- `planned_minutes`, `downtime_minutes`, `units_produced`, `units_defective`, `target_units_per_hour` -> Whole Number

## Data Model

```text
                lines (line_id)
                 /            production_log              monthly_costs
   (daily)                    (monthly)
```

Relationships:

- `lines[line_id]` 1:* `production_log[line_id]`
- `lines[line_id]` 1:* `monthly_costs[line_id]`

There is no dedicated Date table. Monthly downtime is grouped by `production_log[production_month]`, a column added in Power Query:

```m
AddedMonth = Table.AddColumn(ChangedType, "production_month", each Date.StartOfMonth([production_date]), type date)
```

It has to be a source column, not a DAX calculated column. A calculated column in `production_log` closes the dependency graph through `monthly_costs[Cost per Unit]`, which resolves to `[Total Units]`, and refresh fails with a cyclic reference error.

Important grain rule: `production_log` is daily and `monthly_costs` is monthly. Do not relate the two fact tables directly; use `lines` as the shared dimension. Time-based cost visuals use `monthly_costs[cost_month]`, not the production month.

## Measures

```DAX
Total Units = SUM(production_log[units_produced])

Total Defects = SUM(production_log[units_defective])

Good Units = [Total Units] - [Total Defects]

Planned Minutes = SUM(production_log[planned_minutes])

Downtime Minutes = SUM(production_log[downtime_minutes])

Runtime Minutes = [Planned Minutes] - [Downtime Minutes]

Downtime Rate % = DIVIDE([Downtime Minutes], [Planned Minutes])

Availability % = DIVIDE([Runtime Minutes], [Planned Minutes])

Quality % = DIVIDE([Total Units] - [Total Defects], [Total Units])

Defect Rate % = DIVIDE([Total Defects], [Total Units])

Theoretical Units =
SUMX(
    production_log,
    DIVIDE(production_log[planned_minutes] - production_log[downtime_minutes], 60)
        * RELATED(lines[target_units_per_hour])
)

Performance % = DIVIDE([Total Units], [Theoretical Units])

OEE % = [Availability %] * [Performance %] * [Quality %]

Total Cost = SUM(monthly_costs[amount])

Cost per Unit = DIVIDE([Total Cost], [Total Units])

OEE Target = 0.85

OEE Gap = [OEE %] - [OEE Target]

OEE Gap Label = FORMAT([OEE Gap], "+0.0%;-0.0%") & " vs 85% target"

Lines Below OEE Target = COUNTROWS(FILTER(VALUES(lines[line_name]), [OEE %] < [OEE Target]))

Worst OEE Line =
CONCATENATEX(TOPN(1, VALUES(lines[line_name]), [OEE %], ASC), lines[line_name], ", ")

Top Downtime Reason =
CONCATENATEX(TOPN(1, VALUES(production_log[downtime_reason]), [Downtime Minutes], DESC), production_log[downtime_reason], ", ")

Worst Line Availability = CALCULATE([Availability %], TOPN(1, VALUES(lines[line_name]), [OEE %], ASC))

Worst Line Performance = CALCULATE([Performance %], TOPN(1, VALUES(lines[line_name]), [OEE %], ASC))

Worst Line Quality = CALCULATE([Quality %], TOPN(1, VALUES(lines[line_name]), [OEE %], ASC))

OEE Bar Color = IF([OEE %] < [OEE Target], "#D4602E", "#1F4E79")

Materials Cost = CALCULATE([Total Cost], monthly_costs[cost_type] = "Materials")

Materials Share % = DIVIDE([Materials Cost], [Total Cost])

Highest Cost Type =
CONCATENATEX(TOPN(1, VALUES(monthly_costs[cost_type]), [Total Cost], DESC), monthly_costs[cost_type], ", ")
```

Sanity check: `OEE %` by `line_name` should run from about 73.4% for Line 3 to 85.8% for Line 2.

## Pages

All three pages share one grid, so moving between them does not move the furniture.

### Page 1 - Overview

- Header: page title, `lines[line_name]` slicer on the right
- KPI card: `OEE %`, `Availability %`, `Performance %`, `Quality %`
- Left: `Sum of downtime_minutes` by `production_log[production_month]`
- Right: `OEE %` by `lines[line_name]`, sorted descending, bars coloured by `OEE Bar Color`
- Full width: table with `line_name`, `OEE %`, `OEE Gap`, `Downtime Rate %`, `Defect Rate %`, `Total Units`
- Finding: average OEE is 81.2%, below the 85% target, and four of six lines miss it

The KPI card carries OEE next to all three of its factors, so the headline number decomposes on the page rather than standing alone. The target is stated in the chart title and encoded in the bar colour.

### Page 2 - OEE Breakdown

- Header: page title, `lines[line_name]` slicer on the right
- KPI card: `Worst OEE Line`, `Worst Line Availability`, `Worst Line Performance`, `Worst Line Quality`
- Left: `Total Units` by `lines[line_name]`, sorted descending
- Right: `Downtime Minutes` by `production_log[downtime_reason]`, sorted descending
- Full width: table with `line_name`, `Availability %`, `Performance %`, `Quality %`, `OEE %`, `OEE Gap`
- Finding: the worst line loses OEE on availability (79.8%), not on speed (94.6%) or quality (97.1%)

The worst-line cards are driven by `TOPN` rather than hardcoded to Line 3, so the page still reads correctly if the data changes.

### Page 3 - Cost Analysis

- Header: page title, `lines[line_name]` slicer on the right
- KPI cards: `Total Cost`, `Cost per Unit`, `Materials Share %`, `Highest Cost Type`
- Left: `Total Cost` by `monthly_costs[cost_type]`, sorted descending
- Right: stacked column of `Total Cost` by `cost_month` and `cost_type`
- Full width: `Cost per Unit` by `monthly_costs[cost_month]`
- Finding: materials are 47% of spend, the largest cost category

## Design System

Canvas `1280 x 720`, page margin 24px, gutter 16px. The rows close exactly on the canvas:

```text
y=24    header (title left, slicer right)      h=48
y=88    KPI row                                h=112
y=216   two charts side by side                h=208
y=440   detail table, full width               h=256
        bottom margin 24
```

Widths: full `1232`, half `608`, quarter `296`. Slicer at `x=1032`, width `224`.

| Role | Hex |
| --- | --- |
| Accent | `#1F4E79` |
| Good | `#2B7A78` |
| Bad | `#D4602E` |
| Neutral | `#B9C3CF` |
| Text | `#404040` |
| Secondary text | `#6C7A89` |
| Page background | `#F4F6F8` |
| Card border | `#E6EAEF` |
| Card background | `#FFFFFF` |

Cards are white with an `#E6EAEF` border, 8px corner radius and a soft shadow, on the grey page background. Typography is Segoe UI throughout. The theme lives in `IndustryOperationsCost.Report/StaticResources/RegisteredResources/IndustrialPremium.json`; container styling is set there rather than per visual, so the report re-themes in one place.

Conventions:

- Bars sorted descending unless the axis is time
- Data labels on and value axis off on bar charts: fewer axis marks, exact values
- Tables at 10pt with no row padding and no vertical gridlines
- Line charts may use a non-zero baseline; bars always start at zero
- One written finding per page
