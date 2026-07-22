# Customer Retention & Behavior - Python

Generates fake customers and transactions with a realistic churn pattern built in (each customer has their own "stickiness," so cohorts decay over time instead of everyone staying active forever), adds dirty data on purpose, cleans it, and loads it into SQLite.

Other parts: [SQL](../sql)

## What it does

1. Generates 600 customers (signup date, acquisition channel, region) over an 18-month window.
2. Simulates month-by-month buying behavior per customer: each month they're active they buy 1-3 times, then they might churn (stop buying) based on their own retention probability - once churned, they don't come back.
3. Injects dirty data: missing channels, orphaned transactions, duplicate rows, a few bad negative amounts.
4. Cleans it and loads `customers` + `transactions` into SQLite.

## Why simulate churn instead of random transactions

My first instinct was just to generate random transactions per customer, but that doesn't actually produce anything worth analyzing - if every customer keeps buying forever with the same odds every month, there's no retention curve to speak of, just noise. Real cohort analysis needs *some* customers to genuinely stop coming back over time, which is why each customer gets their own "stickiness" here instead.

## Tools

- Python 3.10, pandas, numpy, sqlite3

## How to run

```bash
cd customer_retention_behavior/python
pip install -r requirements.txt
python generate_and_load_data.py
```

## Project Status

🟢 Done
