-- Supply Chain & Inventory Optimization - SQL Analysis
-- Author: Juan Jose Carrascal Pinzon
-- Database: database/supply_chain.db
-- Tables: products, suppliers, inventory_snapshots, purchase_orders
-- ============================================

-- Schema reminder:
-- products(product_id, product_name, category, supplier_id, unit_cost, reorder_point, order_quantity)
-- suppliers(supplier_id, supplier_name, region, nominal_lead_time_days)
-- inventory_snapshots(product_id, snapshot_date, stock_on_hand, stockout) -- weekly, 52 weeks
-- purchase_orders(po_id, product_id, supplier_id, order_date, expected_delivery_date, actual_delivery_date, quantity_ordered)


-- STEP 1: Stockout rate by product
-- Objective: which products run out of stock most often (worst first).
SELECT
    p.product_id
    ,p.product_name
    ,p.category
    ,COUNT(*) AS weeks_tracked
    ,SUM(s.stockout) AS weeks_stocked_out
    ,ROUND(100.0 * SUM(s.stockout) / COUNT(*), 1) AS stockout_rate_pct
FROM inventory_snapshots s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY stockout_rate_pct DESC
LIMIT 15;


-- STEP 2: Supplier on-time delivery performance
-- Objective: which suppliers actually deliver by the date they promised,
-- worst first - this is what "reliability" should mean, not a gut feeling.
SELECT
    sup.supplier_id
    ,sup.supplier_name
    ,sup.region
    ,COUNT(*) AS total_orders
    ,SUM(CASE WHEN po.actual_delivery_date <= po.expected_delivery_date THEN 1 ELSE 0 END) AS on_time_orders
    ,ROUND(100.0 * SUM(CASE WHEN po.actual_delivery_date <= po.expected_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 1) AS on_time_pct
    ,ROUND(AVG(julianday(po.actual_delivery_date) - julianday(po.order_date)), 1) AS avg_actual_lead_days
FROM purchase_orders po
JOIN suppliers sup ON po.supplier_id = sup.supplier_id
GROUP BY sup.supplier_id, sup.supplier_name, sup.region
ORDER BY on_time_pct ASC;


-- STEP 3: Current inventory value by category (CTE)
-- Objective: how much money is sitting on the shelf right now, by category.
WITH latest_snapshot AS (
    SELECT product_id, MAX(snapshot_date) AS latest_date
    FROM inventory_snapshots
    GROUP BY product_id
)
SELECT
    p.category
    ,COUNT(DISTINCT p.product_id) AS products
    ,SUM(s.stock_on_hand) AS total_units_on_hand
    ,ROUND(SUM(s.stock_on_hand * p.unit_cost), 2) AS inventory_value
FROM latest_snapshot ls
JOIN inventory_snapshots s ON ls.product_id = s.product_id AND ls.latest_date = s.snapshot_date
JOIN products p ON s.product_id = p.product_id
GROUP BY p.category
ORDER BY inventory_value DESC;


-- STEP 4 (extra): Purchase orders missing a supplier
-- Objective: data quality check - these can't be scored for on-time
-- delivery in STEP 2 because there's no supplier to attribute them to.
SELECT COUNT(*) AS orders_missing_supplier
FROM purchase_orders
WHERE supplier_id IS NULL;
