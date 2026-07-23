# Data Analysis Projects

Data Analyst with a chemical-engineering background. I built these projects to practice and show what I can do with SQL, Power BI, Python and Excel: querying, cleaning, visualizing, and interpreting data.

**Tools:** SQL · Power BI (DAX, Power Query) · Python (pandas) · Excel

**Contact:** juan.jose.carpi@hotmail.com · [LinkedIn](https://www.linkedin.com/in/juan-jose-carrascal-pinzón-0bba35223)

## Repository structure

Organized by project. Each project has its own folder with a README, and inside it the part built with each tool lives in its own subfolder (`python/`, `sql/`, `excel/`).

```
Data-Analysis-Projects/
├── wastewater_effluent_quality/   (python + sql + power bi)
├── sales_analytics_pipeline/      (python + excel)
├── customer_retention_behavior/   (python + sql)
├── industry_operations_cost/      (python + excel)
├── supply_chain_inventory/        (python + sql)
├── football_transfer_market/      (sql)
├── sql_murder_mystery/            (sql)
└── data_jobs_dashboard/           (power bi)
```

## Projects

**[Wastewater Effluent Quality](./wastewater_effluent_quality)** (Python + SQL + Power BI) - real data from an actual wastewater treatment plant ([UCI dataset](https://archive.ics.uci.edu/dataset/106/water+treatment+plant), 165 days of sensor readings). Python cleans the raw sensor data (missing readings kept as `NULL`, not dropped or guessed), SQL measures compliance and removal efficiency, and a Power BI dashboard puts both into KPI cards and charts. The plant met discharge limits on about 95% of the days, and the biological stage does most of the work (83.6% BOD removal vs 37.8% in the primary settler). This is the project that ties my chemical-engineering background to data work.

- **[Data Jobs Dashboard](./data_jobs_dashboard)** (Power BI) - a dashboard on the 2024 data job market (salaries, distribution, remote work, top skills), in two versions that show how my data modeling and DAX improved between them. Includes screenshots.
- **[Sales & Customer Analytics Pipeline](./sales_analytics_pipeline)** (Python + Excel) - Python generates and cleans a synthetic sales dataset, Excel analyzes it with formulas (SUMIFS/VLOOKUP/LARGE).
- **[Football Transfer Market Analysis](./football_transfer_market)** (SQL) - analysis of real transfer-market data: exploration, quality checks, and business questions with joins and subqueries.
- **[Customer Retention & Behavior](./customer_retention_behavior)** (Python + SQL) - Python simulates a customer base with realistic churn, SQL builds cohort retention curves and RFM segments.
- **[Industry Operations & Cost Optimization](./industry_operations_cost)** (Python + Excel) - Python simulates production lines, Excel calculates OEE and cost per unit by line.
- **[Supply Chain & Inventory Optimization](./supply_chain_inventory)** (Python + SQL) - Python runs a week-by-week inventory simulation, SQL analyzes stockout rates and supplier on-time performance.
- **[SQL Murder Mystery](./sql_murder_mystery)** (SQL) - my first SQL project, before any of the others here: a full investigation solved with SQL (joins, subqueries, aggregations) against a relational database.

## Contact

Juan Jose Carrascal Pinzón
juan.jose.carpi@hotmail.com · [LinkedIn](https://www.linkedin.com/in/juan-jose-carrascal-pinzón-0bba35223)
