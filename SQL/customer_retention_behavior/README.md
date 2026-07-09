# Customer Retention & Behavior - SQL Analysis

Cohort retention and RFM (Recency, Frequency, Monetary) segmentation on top of the database from [Python/customer_retention_behavior](../../Python/customer_retention_behavior).

Other parts: [Python](../../Python/customer_retention_behavior) · [Power BI](../../PowerBI/customer_retention_behavior)

## Tools

- SQLite
- DB Browser for SQLite
- Git / GitHub

## Queries (`analytics_queries.sql`)

1. Cohort retention - % of each signup cohort still buying N months later (CTEs).
2. RFM base metrics - recency, frequency, monetary per customer (CTE).
3. RFM segments - Loyal / Active / At Risk / Churned (CTE).
4. Revenue and customers by acquisition channel.
5. Extra: monthly active customers trend.

## Findings

- Retention drops fast: the July 2023 cohort went from 100% (month 0) to 73.3% (month 1) to 46.7% (month 2) - most of the churn happens in the first couple of months.
- 306 of 600 customers fall into "Churned" (no purchase in 180+ days) - more than half the base.
- "Loyal" customers (recent + frequent) spend on average ~2.4x more than "At Risk" ones.
- Social Media brought in the most customers and the most total revenue, but revenue-per-customer is close across all channels except "Unknown" (missing channel data, worth fixing at the source).

## How to run

```bash
cd SQL/customer_retention_behavior
sqlite3 database/customer_retention.db < analytics_queries.sql
```

## Project Status

🟢 Done
