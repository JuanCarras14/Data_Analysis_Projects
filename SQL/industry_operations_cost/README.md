# Industry Operations & Cost Optimization - SQL Analysis

OEE (Overall Equipment Effectiveness) and cost analysis on top of the database from [Python/industry_operations_cost](../../Python/industry_operations_cost).

Other parts: [Python](../../Python/industry_operations_cost) · [Power BI](../../PowerBI/industry_operations_cost)

## Tools

- SQLite
- DB Browser for SQLite
- Git / GitHub

## Queries (`analytics_queries.sql`)

1. OEE per production line - Availability x Performance x Quality (CTEs).
2. Downtime reasons ranked by total minutes lost.
3. Cost per unit produced, joining daily production rolled up to monthly against monthly costs (CTEs).
4. Total cost by category (labor, energy, maintenance, materials).

## Findings

- OEE ranges from 73.3% (Line 3) to 85.9% (Line 2) - anything above ~85% is generally considered "world class" in manufacturing, so Line 2 is already there and Line 3 has real room to improve.
- Line 3's biggest issue is availability (79.8%), not performance or quality - it's a downtime problem, not a speed or defect problem.
- "Operator Break" and "Changeover" account for more lost minutes combined than "Mechanical Failure" - the biggest time losses aren't breakdowns, they're scheduling/process related.
- Materials is by far the largest cost category (~47% of total spend), well ahead of labor (~35%).

## How to run

```bash
cd SQL/industry_operations_cost
sqlite3 database/operations.db < analytics_queries.sql
```

## Project Status

🟢 Done
