# Customer Retention & Behavior

Cohort retention and RFM segmentation on a simulated customer base with realistic churn built in.

## How each tool is used

- **[Python](./python)** - generates 600 customers over an 18-month window and simulates their month-by-month buying, where each customer can churn based on their own retention probability (so cohorts actually decay instead of everyone staying forever). Injects dirty data, cleans it, and loads `customers` + `transactions` into SQLite.
- **[SQL](./sql)** - retention by signup cohort, recency/frequency/spend per customer, customer segments (Loyal / Active / At Risk / Churned), and revenue by acquisition channel.

## What I found

- Retention decays clearly over time: recent signup cohorts are mostly still active (Oct-Dec 2024: 74-100% still buying), while cohorts from about a year earlier have largely gone quiet (mid-2023: under 10% still active).
- 306 of 600 customers are "Churned" (no purchase in 180+ days) - more than half the base.
- "Loyal" customers spend the most on average (~1,632) - about 1.8x an At-Risk customer and 2.4x a Churned one.
