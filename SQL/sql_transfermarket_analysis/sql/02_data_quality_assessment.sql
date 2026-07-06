/*
Football Transfer Market Analysis
Phase 2: Data Quality Assessment

Objective:
Identify data quality issues that could affect subsequent analysis.
Only confirmed findings are documented in this script.
*/


/*
Objective:
Count missing values in key columns from the players table.

Finding:
Several key attributes contain missing values. These records should
be considered when interpreting analyses based on market value,
club information, or player position.
*/
SELECT
    SUM(CASE
        WHEN position IS NULL
            OR position = 'Missing'
        THEN 1
        ELSE 0
    END) AS missing_position
    , SUM(CASE
        WHEN sub_position IS NULL
            OR sub_position = 'Missing'
        THEN 1
        ELSE 0
    END) AS missing_sub_position
    , SUM(CASE
        WHEN country_of_citizenship IS NULL
            OR country_of_citizenship = 'Missing'
        THEN 1
        ELSE 0
    END) AS missing_country_of_citizenship
    , SUM(CASE
        WHEN market_value_in_eur IS NULL
        THEN 1
        ELSE 0
    END) AS missing_market_value_in_eur
    , SUM(CASE
        WHEN highest_market_value_in_eur IS NULL
        THEN 1
        ELSE 0
    END) AS missing_highest_market_value_in_eur
    , SUM(CASE
        WHEN current_club_name IS NULL
            OR current_club_name = 'Missing'
        THEN 1
        ELSE 0
    END) AS missing_current_club_name
FROM players;


/*
Objective:
Document inconsistent country labels referring to the same country.

Finding:
The dataset contains both "Turkey" and "Türkiye" as separate values.
This inconsistency splits country-level aggregations and should be
normalized before performing country-based analysis.
*/
SELECT
    country_of_citizenship
    , COUNT(*) AS total_players
FROM players
WHERE country_of_citizenship IN ('Turkey', 'Türkiye')
GROUP BY country_of_citizenship;