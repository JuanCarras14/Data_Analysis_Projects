-- Industry Operations & Cost Optimization - SQL Analysis
-- Author: Juan Jose Carrascal Pinzon
-- Database: database/operations.db
-- Tables: lines, production_log, monthly_costs (built by the Python script)
-- ============================================

-- Schema reminder:
-- lines(line_id, line_name, area, target_units_per_hour)
-- production_log(log_id, line_id, production_date, planned_minutes,
--                 downtime_minutes, downtime_reason, units_produced, units_defective)
-- monthly_costs(cost_id, line_id, cost_month, cost_type, amount)


-- STEP 1: OEE per production line (CTEs)
-- Objective: OEE = Availability x Performance x Quality, the standard
-- manufacturing KPI for how well a line is actually running.
-- Availability = time actually running / time planned to run
-- Performance  = actual output rate / target output rate
-- Quality      = good units / total units produced
WITH line_stats AS (
    SELECT
        l.line_id
        ,l.line_name
        ,l.area
        ,l.target_units_per_hour
        ,SUM(p.planned_minutes) AS total_planned_minutes
        ,SUM(p.downtime_minutes) AS total_downtime_minutes
        ,SUM(p.units_produced) AS total_units
        ,SUM(p.units_defective) AS total_defects
    FROM lines l
    JOIN production_log p ON l.line_id = p.line_id
    GROUP BY l.line_id, l.line_name, l.area, l.target_units_per_hour
),
oee AS (
    SELECT
        *
        ,ROUND(1.0 * (total_planned_minutes - total_downtime_minutes) / total_planned_minutes, 3) AS availability
        ,ROUND((total_units / ((total_planned_minutes - total_downtime_minutes) / 60.0)) / target_units_per_hour, 3) AS performance
        ,ROUND(1.0 * (total_units - total_defects) / total_units, 3) AS quality
    FROM line_stats
)
SELECT
    line_name
    ,area
    ,availability
    ,performance
    ,quality
    ,ROUND(availability * performance * quality, 3) AS oee
FROM oee
ORDER BY oee DESC;


-- STEP 2: Downtime reasons
-- Objective: what's actually eating up production time, ranked by total
-- minutes lost (not just how often it happens).
SELECT
    downtime_reason
    ,COUNT(*) AS occurrences
    ,SUM(downtime_minutes) AS total_minutes
FROM production_log
WHERE downtime_minutes > 0
GROUP BY downtime_reason
ORDER BY total_minutes DESC;


-- STEP 3: Cost per unit produced (CTEs)
-- Objective: production_log is daily, monthly_costs is monthly - roll
-- production up to monthly first so the two can be joined on the same grain.
WITH monthly_production AS (
    SELECT
        line_id
        ,strftime('%Y-%m', production_date) AS month
        ,SUM(units_produced) AS units_produced
    FROM production_log
    GROUP BY line_id, month
),
monthly_cost_total AS (
    SELECT
        line_id
        ,cost_month AS month
        ,SUM(amount) AS total_cost
    FROM monthly_costs
    GROUP BY line_id, cost_month
)
SELECT
    mp.line_id
    ,mp.month
    ,mp.units_produced
    ,mc.total_cost
    ,ROUND(mc.total_cost / mp.units_produced, 2) AS cost_per_unit
FROM monthly_production mp
JOIN monthly_cost_total mc ON mp.line_id = mc.line_id AND mp.month = mc.month
ORDER BY mp.line_id, mp.month;


-- STEP 4: Total cost by category
-- Objective: where the money actually goes across the whole plant.
SELECT
    cost_type
    ,ROUND(SUM(amount), 2) AS total_cost
FROM monthly_costs
GROUP BY cost_type
ORDER BY total_cost DESC;
