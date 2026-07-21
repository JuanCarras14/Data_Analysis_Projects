# Industry Operations & Cost Optimization

OEE (Overall Equipment Effectiveness) and cost analysis on a simulated manufacturing plant.

## How each tool is used

- **[Python](./python)** — generates 6 production lines, a year of daily production logs and monthly cost breakdowns, injects dirty data on purpose, and cleans it with pandas. The clean CSVs feed the Excel analysis.
- **[Excel](./excel)** — OEE (Availability × Performance × Quality) per line, downtime reasons ranked, cost per unit, and cost by category, using SUMIF/SUMIFS/RANK.

## What I found

- OEE ranges from 73.3% (Line 3) to 85.8% (Line 2) — Line 2 is already around "world class", Line 3 has real room to improve.
- Line 3's main issue is availability (79.8%) — a downtime problem, not speed or defects.
- Operator breaks and changeovers lose more minutes combined than mechanical failures.
- Materials is the largest cost category (~47% of spend), well ahead of labor (~35%).
