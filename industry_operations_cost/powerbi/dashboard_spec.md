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
                 /            \
production_log              monthly_costs
   (daily)                    (monthly)
      |
   Date (production_date)
```

Relationships:

- `lines[line_id]` 1:* `production_log[line_id]`
- `lines[line_id]` 1:* `monthly_costs[line_id]`
- `Date[Date]` 1:* `production_log[production_date]`

Date table:

```DAX
Date = CALENDAR(MIN(production_log[production_date]), MAX(production_log[production_date]))
Year-Month = FORMAT('Date'[Date], "yyyy-mm")
```

Important grain rule: `production_log` is daily and `monthly_costs` is monthly. Do not relate the two fact tables directly; use `lines` as the shared dimension. Time-based cost visuals should use `monthly_costs[cost_month]`, not `Date[Year-Month]`.

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

Materials Cost = CALCULATE([Total Cost], monthly_costs[cost_type] = "Materials")

Materials Share % = DIVIDE([Materials Cost], [Total Cost])

Highest Cost Type =
CONCATENATEX(TOPN(1, VALUES(monthly_costs[cost_type]), [Total Cost], DESC), monthly_costs[cost_type], ", ")
```

Sanity check: `OEE %` by `line_name` should run from about 73.4% for Line 3 to 85.8% for Line 2.

## Pages

### Page 1 - Overview

- Slicer: `lines[line_name]`
- Cards: `OEE %`, `Availability %`, `Performance %`, `Lines Below OEE Target`
- Main chart: `Downtime Minutes` by `Date[Year-Month]`
- Detail left: `OEE %` by `lines[line_name]`, sorted ascending, reference line at 85%
- Detail right: `Total Units` by `lines[line_name]`
- Finding: downtime varies through the year and keeps the OEE story tied to operating time lost

### Page 2 - OEE Breakdown

- Slicer: `lines[line_name]`
- Cards: lowest OEE line, Line 3 availability, Line 3 performance, Line 3 quality
- Cards: `Worst OEE Line`, `Line 3 Availability`, `Line 3 Performance`, `Top Downtime Reason`
- Main visual: table with `line_name`, `area`, `Availability %`, `Performance %`, `Quality %`, `OEE %`, `OEE Gap`
- Detail left: `Downtime Minutes` by `downtime_reason`, sorted descending
- Detail right: stacked bar with `downtime_reason`, `Downtime Minutes`, and `line_name`
- Finding: Line 3's issue is availability, not speed or defects

### Page 3 - Cost Analysis

- Slicer: `lines[line_name]`
- Cards: `Total Cost`, `Cost per Unit`, `Materials Share %`, `Highest Cost Type`
- Main left: `Total Cost` by `monthly_costs[cost_type]`
- Main right: stacked column of `Total Cost` by `monthly_costs[cost_month]` and `cost_type`
- Detail full width: `Cost per Unit` by `monthly_costs[cost_month]`, legend `line_name`
- Finding: materials are the largest cost category

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
