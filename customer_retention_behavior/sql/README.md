# Customer Retention & Behavior - SQL Analysis

Cohort retention and RFM (Recency, Frequency, Monetary) segmentation on top of the database from [Python/customer_retention_behavior](../python).

Other parts: [Python](../python)

## Tools

- SQLite
- DB Browser for SQLite

## Queries (`analytics_queries.sql`)

1. Retention by signup cohort - % of each signup month still active (bought in the last 60 days).
2. Recency, frequency and spend per customer (top 20 by spend).
3. Customer segments - Loyal / Active / At Risk / Churned.
4. Revenue and customers by acquisition channel.
5. Extra: monthly active customers trend.

## Findings

- Retention decays clearly over time: recent signup cohorts are mostly still active (Oct-Dec 2024: 74-100% bought in the last 60 days), while cohorts from about a year earlier have largely gone quiet (mid-2023: under 10% still active).
- 306 of 600 customers fall into "Churned" (no purchase in 180+ days) - more than half the base.
- "Loyal" customers spend the most on average (~1,632) - about 1.8x an At-Risk customer and 2.4x a Churned one.
- Social Media brought in the most customers and the most total revenue, but revenue-per-customer is close across all channels except "Unknown" (missing channel data, worth fixing at the source).

## How to run

```bash
cd customer_retention_behavior/sql
sqlite3 database/customer_retention.db < analytics_queries.sql
```

## Project Status

🟢 Done
