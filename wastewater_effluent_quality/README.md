# Wastewater Effluent Quality

The project I'm most proud of: data analysis on real data from an actual urban wastewater treatment plant ([UCI dataset](https://archive.ics.uci.edu/dataset/106/water+treatment+plant), 165 days of sensor readings). It connects my chemical-engineering background with the data toolset.

## How each tool is used

- **[Python](./python)** — loads and cleans the raw sensor feed with pandas. Missing readings are kept as `NULL` instead of dropped or guessed, since a gap can mean a real plant problem, then the clean data is loaded into SQLite.
- **[SQL](./sql)** — queries the database to measure compliance and removal efficiency by treatment stage: summary stats, days over the limits, compliance rate (CTE), primary vs secondary comparison, a missing-data audit, and a 7-day rolling average (window function).

## What I found

- The plant met discharge limits on about 95% of the days (only ~5% went over at least one reference limit).
- The biological (secondary) stage does most of the work — around 83.6% average BOD removal, vs ~37.8% in the primary settler.
- The days tagged as "overloaded" actually had the best average removal, which I'd want to look into further.
