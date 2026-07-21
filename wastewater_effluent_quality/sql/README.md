# Wastewater Effluent Quality - SQL Analysis

SQL analysis on real data from an urban wastewater treatment plant (165 days, [UCI dataset](https://archive.ics.uci.edu/dataset/106/water+treatment+plant)). The database is built by [Python/wastewater_effluent_quality](../python) and included here, ready to query.

Other parts: [Python](../python)

## Dataset

Real daily sensor readings from an urban wastewater plant: influent quality, primary settler, secondary (biological) settler, and effluent quality, plus removal efficiency at each stage.

## Tools

- SQLite
- DB Browser for SQLite
- Git / GitHub

## Queries (`analytics_queries.sql`)

1. Effluent quality summary (averages).
2. Days that exceeded reference discharge limits.
3. Overall compliance rate.
4. Effluent quality by plant operating status.
5. Primary vs secondary stage - which one removes more BOD.
6. Missing sensor readings audit.
7. Average effluent BOD by month.

## Findings

- Average effluent: 19.7 mg/L BOD, 89.7 mg/L COD, 23.8 mg/L SS - within the reference limits used here (40 / 160 / 60 mg/L) on average.
- 4.9% of monitored days exceeded at least one of those reference limits.
- The secondary (biological) stage does most of the work: ~83.6% average BOD removal vs ~37.8% in the primary settler.
- Days flagged as "overloaded" (`Normal_situation_over`) actually had the *best* average BOD removal (90.8%) - worth digging into further rather than assuming overload always means worse performance.

## How to run

```bash
cd wastewater_effluent_quality/sql
sqlite3 database/wastewater.db < analytics_queries.sql
```

## Project Status

🟢 Done
