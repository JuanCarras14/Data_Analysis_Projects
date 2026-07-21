/*
Football Transfer Market Analysis
Phase 3: Business Analysis

Objective:
Answer business questions about transfer spending, clubs, and player
valuation by joining transfers with players, clubs, and competitions.
*/


/*
Objective:
Total transfer spending and number of transfers per season, to see
how the market has grown over time.
*/
SELECT
    transfer_season
    , ROUND(SUM(CAST(transfer_fee AS REAL)), 0) AS total_spent
    , COUNT(*) AS total_transfers
FROM transfers
WHERE transfer_fee IS NOT NULL
GROUP BY transfer_season
ORDER BY transfer_season;


/*
Objective:
Top 10 most expensive transfers in the dataset.
*/
SELECT
    player_name
    , transfer_season
    , from_club_name
    , to_club_name
    , CAST(transfer_fee AS REAL) AS transfer_fee
FROM transfers
WHERE transfer_fee IS NOT NULL
ORDER BY transfer_fee DESC
LIMIT 10;


/*
Objective:
Top 10 clubs by total transfer spending (money spent buying players).
*/
SELECT
    to_club_name
    , ROUND(SUM(CAST(transfer_fee AS REAL)), 0) AS total_spent
    , COUNT(*) AS players_bought
FROM transfers
WHERE transfer_fee IS NOT NULL
GROUP BY to_club_name
ORDER BY total_spent DESC
LIMIT 10;


/*
Objective:
Top 10 clubs by total income from selling players.
*/
SELECT
    from_club_name
    , ROUND(SUM(CAST(transfer_fee AS REAL)), 0) AS total_income
    , COUNT(*) AS players_sold
FROM transfers
WHERE transfer_fee IS NOT NULL
GROUP BY from_club_name
ORDER BY total_income DESC
LIMIT 10;


/*
Objective:
Net transfer balance per club (income from sales minus money spent
buying players). Built with two CTEs, one for spending and one for
income, joined together on club name.

Finding:
The 10 clubs below all have a negative balance, meaning they spend
far more on buying players than they make selling them.
*/
WITH spending AS (
    SELECT
        to_club_name AS club_name
        , SUM(CAST(transfer_fee AS REAL)) AS total_spent
    FROM transfers
    WHERE transfer_fee IS NOT NULL
    GROUP BY to_club_name
),
income AS (
    SELECT
        from_club_name AS club_name
        , SUM(CAST(transfer_fee AS REAL)) AS total_income
    FROM transfers
    WHERE transfer_fee IS NOT NULL
    GROUP BY from_club_name
)
SELECT
    s.club_name
    , s.total_spent
    , COALESCE(i.total_income, 0) AS total_income
    , ROUND(COALESCE(i.total_income, 0) - s.total_spent, 0) AS net_balance
FROM spending s
LEFT JOIN income i ON s.club_name = i.club_name
ORDER BY net_balance ASC
LIMIT 10;


/*
Objective:
Average transfer fee by player position (joining transfers to players).
*/
SELECT
    p.position
    , ROUND(AVG(CAST(t.transfer_fee AS REAL)), 0) AS avg_transfer_fee
    , COUNT(*) AS total_transfers
FROM transfers t
JOIN players p ON t.player_id = p.player_id
WHERE t.transfer_fee IS NOT NULL
    AND p.position <> 'Missing'
GROUP BY p.position
ORDER BY avg_transfer_fee DESC;


/*
Objective:
Top 10 competitions by total transfer spending, joining transfers to
clubs (to get the buying club) and clubs to competitions.
*/
SELECT
    comp.name AS competition_name
    , comp.country_name
    , ROUND(SUM(CAST(t.transfer_fee AS REAL)), 0) AS total_spent
FROM transfers t
JOIN clubs c ON t.to_club_id = c.club_id
JOIN competitions comp ON c.domestic_competition_id = comp.competition_id
WHERE t.transfer_fee IS NOT NULL
GROUP BY comp.name, comp.country_name
ORDER BY total_spent DESC
LIMIT 10;
