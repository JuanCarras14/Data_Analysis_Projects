# Data Analysis Projects

Chemical engineer moving into data analysis. I built these projects to practice and show what I can do with SQL, Power BI, Python and Excel — querying, cleaning, visualizing, and actually interpreting the data.

**Tools:** SQL · Power BI (DAX, Power Query) · Python (pandas) · Excel
**Contact:** juan.jose.carpi@hotmail.com · [LinkedIn](https://www.linkedin.com/in/juan-jose-carrascal-pinzón-0bba35223)

## Repository structure

```
Data-Analysis-Projects/
├── SQL/          Query based projects and exercises
├── PowerBI/      Interactive dashboards and reports
├── Python/       Data analysis and scripts
└── Excel/        Models and analysis in Excel
```

Each folder contains independent projects, each with its own README describing the objective, process, and results. Some projects use more than one tool (e.g. **wastewater_effluent_quality**, **sales_analytics_pipeline**); for those, each tool's part lives in its own folder under the same project name, with its own README linking to the other parts.

## Projects

**Wastewater Effluent Quality** — the one I'm most proud of, because it uses real data from an actual wastewater treatment plant ([UCI dataset](https://archive.ics.uci.edu/dataset/106/water+treatment+plant), 165 days of sensor readings) and it connects to my engineering background. [Python](./Python/wastewater_effluent_quality) loads and cleans the raw sensor data — I left missing readings as `NULL` instead of dropping or guessing them, since a gap can mean a real plant issue — and [SQL](./SQL/wastewater_effluent_quality) checks compliance and removal efficiency by stage. A few things I found: the plant met discharge limits on about 95% of the days, and the biological stage does most of the work (~83.6% average BOD removal vs ~37.8% in the primary settler). One result I didn't expect: the days marked as "overloaded" actually had the best removal, which I'd like to look into further.

- **[Data Jobs Dashboard](./PowerBI/data_jobs_dashboard)** — a Power BI dashboard on the 2024 data job market (salaries, distribution, remote work, top skills), in two versions that show how my data modeling and DAX improved between them. Includes screenshots.
- **[Sales & Customer Analytics Pipeline](./Python/sales_analytics_pipeline)** — [Python](./Python/sales_analytics_pipeline) generates and cleans a fake sales dataset, [Excel](./Excel/sales_analytics_pipeline) analyzes it with SUMIFS/VLOOKUP/LARGE formulas. Power BI dashboard still in progress.
- **[Football Transfer Market Analysis](./SQL/sql_transfermarket_analysis)** — SQL analysis on real transfer market data: exploration, quality checks, and business questions with joins and CTEs.
- **[Customer Retention & Behavior](./Python/customer_retention_behavior)** — [Python](./Python/customer_retention_behavior) simulates a customer base with realistic churn, [SQL](./SQL/customer_retention_behavior) builds cohort retention curves and RFM segments.
- **[Industry Operations & Cost Optimization](./Python/industry_operations_cost)** — [Python](./Python/industry_operations_cost) simulates production lines with different reliability, [Excel](./Excel/industry_operations_cost) calculates OEE (Availability × Performance × Quality) and cost per unit by line.
- **[Supply Chain & Inventory Optimization](./Python/supply_chain_inventory)** — [Python](./Python/supply_chain_inventory) runs a week-by-week inventory simulation (demand, reorder points, supplier delays), [SQL](./SQL/supply_chain_inventory) analyzes stockout rates and supplier on-time performance.
- **[SQL Murder Mystery](./SQL/sql_murder_mystery)** — a full investigation solved with SQL (joins, subqueries, aggregations) against a relational database.

## Contact

Juan Jose Carrascal Pinzón
juan.jose.carpi@hotmail.com · [LinkedIn](https://www.linkedin.com/in/juan-jose-carrascal-pinzón-0bba35223)
