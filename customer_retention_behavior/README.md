# Customer Retention & Behavior

Cohort retention and RFM segmentation on a simulated customer base with realistic churn built in.

## How each tool is used

- **[Python](./python)** - generates 600 customers over an 18-month window and simulates their month-by-month buying, where each customer can churn based on their own retention probability (so cohorts actually decay instead of everyone staying forever). Injects dirty data, cleans it, and loads `customers` + `transactions` into SQLite.
- **[SQL](./sql)** - cohort retention curves, RFM base metrics and segments (Loyal / Active / At Risk / Churned), and revenue by acquisition channel, using CTEs.

## What I found

- Retention drops fast: the July 2023 cohort went from 100% to 73.3% to 46.7% over the first two months.
- 306 of 600 customers are "Churned" (no purchase in 180+ days) - more than half the base.
- "Loyal" customers spend on average ~2.4x more than "At Risk" ones.
