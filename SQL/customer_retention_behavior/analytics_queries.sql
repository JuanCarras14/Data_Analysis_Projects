-- Customer Retention & Behavior - SQL Analysis
-- Author: Juan Jose Carrascal Pinzon
-- Database: database/customer_retention.db
-- Tables: customers, transactions (built by the Python script)
-- ============================================

-- Schema reminder:
-- customers(customer_id, signup_date, acquisition_channel, region)
-- transactions(transaction_id, customer_id, transaction_date, category, amount)
-- "2024-12-31" is used below as the analysis cutoff date ("today").


-- STEP 1: Cohort retention (CTEs)
-- Objective: group customers by the month of their first transaction (their
-- "cohort"), then track what % of each cohort is still buying N months later.
WITH customer_cohort AS (
    SELECT
        customer_id
        ,strftime('%Y-%m', MIN(transaction_date)) AS cohort_month
    FROM transactions
    GROUP BY customer_id
),
tx_with_cohort AS (
    SELECT
        t.customer_id
        ,c.cohort_month
        ,(CAST(strftime('%Y', t.transaction_date) AS INT) - CAST(substr(c.cohort_month, 1, 4) AS INT)) * 12
            + (CAST(strftime('%m', t.transaction_date) AS INT) - CAST(substr(c.cohort_month, 6, 2) AS INT)) AS month_number
    FROM transactions t
    JOIN customer_cohort c ON t.customer_id = c.customer_id
),
cohort_size AS (
    SELECT cohort_month, COUNT(DISTINCT customer_id) AS total_customers
    FROM tx_with_cohort
    WHERE month_number = 0
    GROUP BY cohort_month
)
SELECT
    tw.cohort_month
    ,tw.month_number
    ,COUNT(DISTINCT tw.customer_id) AS active_customers
    ,cs.total_customers AS cohort_size
    ,ROUND(100.0 * COUNT(DISTINCT tw.customer_id) / cs.total_customers, 1) AS retention_pct
FROM tx_with_cohort tw
JOIN cohort_size cs ON tw.cohort_month = cs.cohort_month
GROUP BY tw.cohort_month, tw.month_number
ORDER BY tw.cohort_month, tw.month_number;


-- STEP 2: RFM base metrics (Recency, Frequency, Monetary)
-- Objective: one row per customer summarizing how recently, how often, and
-- how much they've bought - the standard inputs for customer segmentation.
WITH customer_stats AS (
    SELECT
        customer_id
        ,MAX(transaction_date) AS last_purchase
        ,COUNT(*) AS frequency
        ,ROUND(SUM(amount), 2) AS monetary
        ,CAST(julianday('2024-12-31') - julianday(MAX(transaction_date)) AS INT) AS recency_days
    FROM transactions
    GROUP BY customer_id
)
SELECT * FROM customer_stats
ORDER BY monetary DESC
LIMIT 20;


-- STEP 3: RFM segments
-- Objective: turn the raw R/F/M numbers into labels a non-technical
-- stakeholder can act on.
WITH customer_stats AS (
    SELECT
        customer_id
        ,COUNT(*) AS frequency
        ,ROUND(SUM(amount), 2) AS monetary
        ,CAST(julianday('2024-12-31') - julianday(MAX(transaction_date)) AS INT) AS recency_days
    FROM transactions
    GROUP BY customer_id
),
segmented AS (
    SELECT
        *
        ,CASE
            WHEN recency_days <= 60 AND frequency >= 5 THEN 'Loyal'
            WHEN recency_days <= 60 THEN 'Active'
            WHEN recency_days BETWEEN 61 AND 180 THEN 'At Risk'
            ELSE 'Churned'
        END AS segment
    FROM customer_stats
)
SELECT
    segment
    ,COUNT(*) AS customers
    ,ROUND(AVG(frequency), 1) AS avg_orders
    ,ROUND(AVG(monetary), 2) AS avg_monetary
FROM segmented
GROUP BY segment
ORDER BY avg_monetary DESC;


-- STEP 4: Revenue and customers by acquisition channel
-- Objective: which channel brings in customers who actually spend.
SELECT
    c.acquisition_channel
    ,COUNT(DISTINCT c.customer_id) AS customers
    ,ROUND(SUM(t.amount), 2) AS total_revenue
    ,ROUND(SUM(t.amount) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
FROM customers c
JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.acquisition_channel
ORDER BY total_revenue DESC;


-- STEP 5 (extra): Monthly active customers
-- Objective: simple trend of how many distinct customers bought each month.
SELECT
    strftime('%Y-%m', transaction_date) AS month
    ,COUNT(DISTINCT customer_id) AS active_customers
    ,ROUND(SUM(amount), 2) AS revenue
FROM transactions
GROUP BY month
ORDER BY month;
