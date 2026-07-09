# Industry Operations & Cost Optimization - Excel Analysis

OEE (Overall Equipment Effectiveness) and cost analysis on top of the clean CSVs from [Python/industry_operations_cost](../../Python/industry_operations_cost), using formulas only (no SQL, no Power BI build yet).

Other parts: [Python](../../Python/industry_operations_cost) · [Power BI](../../PowerBI/industry_operations_cost)

## Tools

- Microsoft Excel
- VLOOKUP, SUMIF/SUMIFS, RANK

## Workbook (`operations_analysis.xlsx`)

- **Lines / Production Log / Monthly Costs**: the clean tables, imported as-is. `Production Log` adds one helper column (`log_month`) so daily rows can be matched to monthly costs.
- **OEE by Line**: Availability x Performance x Quality per line, built from SUMIF totals (planned minutes, downtime, units, defects) per line.
- **Downtime Reasons**: total minutes lost per reason, with a `RANK` column so the worst reason is easy to spot without manually sorting.
- **Cost per Unit**: production rolled up from daily to monthly (SUMIFS by line + month) so it can be matched against the monthly cost table, then cost divided by units.
- **Cost by Category**: total spend by cost type (Labor, Energy, Maintenance, Materials).

## Findings

- OEE ranges from 73.3% (Line 3) to 85.8% (Line 2) - anything above ~85% is generally considered "world class" in manufacturing, so Line 2 is already there and Line 3 has real room to improve.
- Line 3's biggest issue is availability (79.8%), not performance or quality - it's a downtime problem, not a speed or defect problem.
- "Operator Break" and "Changeover" account for more lost minutes combined than "Mechanical Failure" - the biggest time losses aren't breakdowns, they're scheduling/process related.
- Materials is by far the largest cost category (~47% of total spend), well ahead of labor (~35%).

## How to run

Open `operations_analysis.xlsx` - all formulas recalculate automatically. To rebuild from scratch, regenerate the CSVs with the Python script and re-import them into the `Lines`/`Production Log`/`Monthly Costs` sheets.

## Project Status

🟢 Done
