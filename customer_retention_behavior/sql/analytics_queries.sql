-- Customer Retention & Behavior - SQL Analysis
-- Author: Juan Jose Carrascal Pinzon
-- Database: database/customer_retention.db
-- Tables: customers, transactions (built by the Python script)
-- ============================================

-- Schema reminder:
-- customers(customer_id, signup_date, acquisition_channel, region)
-- transactions(transaction_id, customer_id, transaction_date, category, amount)
-- "2024-12-31" is used below as the analysis cutoff date ("today").


-- STEP 1: Retention by signup cohort
-- Objective: group customers by the month they signed up, then check how many
-- of each group are still active (bought in the last 60 days before the cutoff).
-- A LEFT JOIN keeps every customer; a CASE inside COUNT(DISTINCT ...) counts only
-- the ones with a recent purchase.
SELECT
    strftime('%Y-%m', c.signup_date) AS signup_month
    ,COUNT(DISTINCT c.customer_id) AS customers
    ,COUNT(DISTINCT CASE
        WHEN julianday('2024-12-31') - julianday(t.transaction_date) <= 60
        THEN c.customer_id END) AS still_active
    ,ROUND(100.0 * COUNT(DISTINCT CASE
        WHEN julianday('2024-12-31') - julianday(t.transaction_date) <= 60
        THEN c.customer_id END) / COUNT(DISTINCT c.customer_id), 1) AS active_pct
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY signup_month
ORDER BY signup_month;


-- STEP 2: Recency, frequency and spend per customer (top 20 by spend)
-- Objective: one row per customer summarizing how recently, how often and how
-- much they bought - the standard inputs for customer segmentation.
SELECT
    customer_id
    ,MAX(transaction_date) AS last_purchase
    ,COUNT(*) AS frequency
    ,ROUND(SUM(amount), 2) AS monetary
    ,CAST(julianday('2024-12-31') - julianday(MAX(transaction_date)) AS INT) AS recency_days
FROM transactions
GROUP BY customer_id
ORDER BY monetary DESC
LIMIT 20;


-- STEP 3: Customer segments (Loyal / Active / At Risk / Churned)
-- Objective: turn the raw recency/frequency numbers into labels a non-technical
-- stakeholder can act on, then count and average each segment.
-- The inner query builds one row per customer with a segment label; the outer
-- query groups those rows by segment.
SELECT
    segment
    ,COUNT(*) AS customers
    ,ROUND(AVG(frequency), 1) AS avg_orders
    ,ROUND(AVG(monetary), 2) AS avg_monetary
FROM (
    SELECT
        customer_id
        ,COUNT(*) AS frequency
        ,ROUND(SUM(amount), 2) AS monetary
        ,CAST(julianday('2024-12-31') - julianday(MAX(transaction_date)) AS INT) AS recency_days
        ,CASE
            WHEN CAST(julianday('2024-12-31') - julianday(MAX(transaction_date)) AS INT) <= 60
                 AND COUNT(*) >= 5 THEN 'Loyal'
            WHEN CAST(julianday('2024-12-31') - julianday(MAX(transaction_date)) AS INT) <= 60 THEN 'Active'
            WHEN CAST(julianday('2024-12-31') - julianday(MAX(transaction_date)) AS INT) BETWEEN 61 AND 180 THEN 'At Risk'
            ELSE 'Churned'
        END AS segment
    FROM transactions
    GROUP BY customer_id
) AS customer_stats
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
