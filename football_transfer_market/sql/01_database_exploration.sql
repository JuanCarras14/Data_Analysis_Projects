/*
Football Transfer Market Analysis
Phase 1: Data Exploration

Objective:
Explore the players table to understand the distribution of players
across positions, sub-positions, countries of citizenship, and market value.
This phase establishes a baseline understanding of the dataset before
moving into business analysis.
*/


/*
Objective:
Count how many players exist per main position.
*/
SELECT
    position
    , COUNT(*) AS total_players
FROM players
GROUP BY position
ORDER BY total_players DESC;


/*
Objective:
Break down player counts by position and sub-position,
excluding records with a missing sub-position.
*/
SELECT
    position
    , sub_position
    , COUNT(*) AS total_players
FROM players
WHERE sub_position IS NOT NULL
GROUP BY
    position
    , sub_position
ORDER BY total_players DESC;


/*
Objective:
Identify the top 10 countries of citizenship by number of players
in the dataset.
*/
SELECT
    country_of_citizenship
    , COUNT(*) AS total_players
FROM players
GROUP BY country_of_citizenship
ORDER BY total_players DESC
LIMIT 10;


/*
Objective:
For the top 5 countries by player count, break down how many
players each country has per position.
*/
SELECT
    country_of_citizenship
    , position
    , COUNT(*) AS total_players
FROM players
WHERE country_of_citizenship IN
(
    SELECT country_of_citizenship
    FROM players
    GROUP BY country_of_citizenship
    ORDER BY COUNT(*) DESC
    LIMIT 5
)
GROUP BY
    country_of_citizenship
    , position
ORDER BY total_players DESC;


/*
Objective:
Calculate the average market value per position and sub-position,
excluding players with a missing position.
*/
SELECT
    position
    , sub_position
    , ROUND(AVG(market_value_in_eur), 0) AS avg_market_value
FROM players
WHERE position <> 'Missing'
GROUP BY
    position
    , sub_position
ORDER BY avg_market_value DESC;


/*
Objective:
Calculate the average market value per country of citizenship,
keeping only countries with at least 200 players in the dataset.
This filters out countries with very few players, which would
otherwise produce unreliable or misleading average values.
*/
SELECT
    country_of_citizenship
    , ROUND(AVG(market_value_in_eur), 0) AS avg_market_value
FROM players
WHERE position <> 'Missing'
AND market_value_in_eur IS NOT NULL
AND country_of_citizenship IS NOT NULL
GROUP BY country_of_citizenship
HAVING COUNT(*) >= 200
ORDER BY avg_market_value DESC;


/*
Known data quality issue (to be addressed in 02_data_quality_assessment.sql):
"Turkey" and "Türkiye" appear as separate values for country_of_citizenship
when they refer to the same country. This affects any country-level
aggregation until the dataset is normalized.
*/