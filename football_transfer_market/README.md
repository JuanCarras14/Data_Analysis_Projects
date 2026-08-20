# Football Transfer Market Analysis

SQL analysis of the football transfer market: what clubs spend, how player valuations behave, and how spending has shifted across seasons and leagues.

## Dataset

The [Transfermarkt football dataset](https://www.kaggle.com/datasets/davidcariboo/player-scores) - players, clubs, competitions, appearances, valuations and transfers. The CSVs and the SQLite database built from them are ~1.4 GB and are not committed; download the dataset and load the CSVs into a SQLite database named `database/transfermarket.db` to run the queries.

## Tools

- SQLite
- DB Browser for SQLite

## Queries

The analysis runs in three stages, one file each:

1. **[`01_database_exploration.sql`](sql/01_database_exploration.sql)** - table sizes, key columns, and how the tables relate.
2. **[`02_data_quality_assessment.sql`](sql/02_data_quality_assessment.sql)** - nulls, duplicates, orphaned foreign keys and out-of-range values, checked before trusting any aggregate.
3. **[`03_business_analysis.sql`](sql/03_business_analysis.sql)** - the actual questions, using joins, subqueries and window functions.

## What I found

- Transfer spending has grown sharply season over season, with the biggest jumps in the last decade.
- The most expensive transfer in the dataset is Neymar, Barcelona to PSG, EUR 222M (17/18).
- Chelsea, Man City and Man Utd are the top spenders overall.
- Every top-10 spending club runs a negative net balance - they spend far more buying than they recover selling.
- Attackers command the highest average transfer fee, goalkeepers the lowest.
- Premier League clubs outspend every other league by a wide margin, ahead of Serie A and LaLiga.
