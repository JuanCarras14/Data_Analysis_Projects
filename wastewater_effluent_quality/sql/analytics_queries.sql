-- Wastewater Effluent Quality - SQL Analysis
-- Author: Juan Jose Carrascal Pinzon
-- Database: database/wastewater.db
-- Table: plant_readings (real UCI water treatment plant data, 165 days)
-- ============================================

-- Schema reminder: influent_* (raw water in), primary_*/secondary_* (mid-process),
-- effluent_* (treated water out), removal_*_pct (% removed at each stage).
-- Reference limits used below (BOD 40 mg/L, COD 160 mg/L, SS 60 mg/L) are
-- generic secondary-treatment discharge limits for illustration, not a
-- specific permit - see the project README.


-- STEP 1: Effluent quality summary
-- Objective: what does the treated water look like on average?
SELECT
    COUNT(*) AS total_days
    ,ROUND(AVG(effluent_bod_mgl), 1) AS avg_effluent_bod
    ,ROUND(AVG(effluent_cod_mgl), 1) AS avg_effluent_cod
    ,ROUND(AVG(effluent_ss_mgl), 1) AS avg_effluent_ss
    ,ROUND(AVG(removal_bod_global_pct), 1) AS avg_bod_removal_pct
    ,ROUND(AVG(removal_cod_global_pct), 1) AS avg_cod_removal_pct
FROM plant_readings;


-- STEP 2: Days that exceeded reference discharge limits
-- Objective: flag individual days where effluent quality was out of range.
SELECT
    day_id
    ,sample_date
    ,effluent_bod_mgl
    ,effluent_cod_mgl
    ,effluent_ss_mgl
    ,CASE WHEN effluent_bod_mgl > 40 THEN 'Y' ELSE 'N' END AS bod_exceeds
    ,CASE WHEN effluent_cod_mgl > 160 THEN 'Y' ELSE 'N' END AS cod_exceeds
    ,CASE WHEN effluent_ss_mgl > 60 THEN 'Y' ELSE 'N' END AS ss_exceeds
FROM plant_readings
WHERE effluent_bod_mgl > 40 OR effluent_cod_mgl > 160 OR effluent_ss_mgl > 60
ORDER BY day_id;


-- STEP 3: Compliance rate (CTE)
-- Objective: what % of monitored days broke at least one of the 3 limits above.
WITH flagged AS (
    SELECT
        day_id
        ,CASE WHEN effluent_bod_mgl > 40 OR effluent_cod_mgl > 160 OR effluent_ss_mgl > 60
              THEN 1 ELSE 0 END AS exceeds_limits
    FROM plant_readings
    WHERE effluent_bod_mgl IS NOT NULL OR effluent_cod_mgl IS NOT NULL OR effluent_ss_mgl IS NOT NULL
)
SELECT
    COUNT(*) AS days_checked
    ,SUM(exceeds_limits) AS days_over_limit
    ,ROUND(100.0 * SUM(exceeds_limits) / COUNT(*), 1) AS pct_days_over_limit
FROM flagged;


-- STEP 4: Effluent quality by plant operating status
-- Objective: the dataset tags each day as Normal / Normal_over (overloaded) /
-- Normal_low_influent - check whether that actually shows up in the numbers.
SELECT
    plant_status
    ,COUNT(*) AS days
    ,ROUND(AVG(effluent_bod_mgl), 1) AS avg_effluent_bod
    ,ROUND(AVG(effluent_ss_mgl), 1) AS avg_effluent_ss
    ,ROUND(AVG(removal_bod_global_pct), 1) AS avg_bod_removal_pct
FROM plant_readings
GROUP BY plant_status
ORDER BY avg_bod_removal_pct DESC;


-- STEP 5: Which stage does the actual cleaning?
-- Objective: compare BOD removal in the primary settler vs the secondary
-- (biological) stage, to see where most of the treatment work happens.
SELECT
    ROUND(AVG(removal_bod_primary_pct), 1) AS avg_removal_primary_stage
    ,ROUND(AVG(removal_bod_secondary_pct), 1) AS avg_removal_secondary_stage
FROM plant_readings;


-- STEP 6: Missing sensor readings audit
-- Objective: this is real sensor data, so some days are missing readings.
-- Counting gaps per column instead of hiding them.
SELECT 'influent_bod_mgl' AS column_name, COUNT(*) - COUNT(influent_bod_mgl) AS missing_days FROM plant_readings
UNION ALL
SELECT 'effluent_bod_mgl', COUNT(*) - COUNT(effluent_bod_mgl) FROM plant_readings
UNION ALL
SELECT 'removal_bod_global_pct', COUNT(*) - COUNT(removal_bod_global_pct) FROM plant_readings;


-- STEP 7: 7-day rolling average of effluent BOD (window function)
-- Objective: daily readings are noisy - a rolling average makes the real
-- trend easier to see than one bad/good day.
SELECT
    day_id
    ,sample_date
    ,effluent_bod_mgl
    ,ROUND(AVG(effluent_bod_mgl) OVER (ORDER BY day_id ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) AS bod_7day_avg
FROM plant_readings
ORDER BY day_id;
