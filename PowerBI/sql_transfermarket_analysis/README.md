# Football Transfer Market Analysis - Power BI Dashboard

Plan for turning the SQL analysis into a dashboard. Uses the same database as [SQL/sql_transfermarket_analysis](../../SQL/sql_transfermarket_analysis).

## Connecting the data

Get Data -> ODBC/SQLite, pointing to `../../SQL/sql_transfermarket_analysis/database/transfermarket.db`. Only import these 4 tables (the rest aren't needed for this dashboard):

- `transfers`
- `clubs`
- `players`
- `competitions`

In Power Query, change `transfer_fee` from text to **Decimal Number** - it's stored as text in the database (e.g. `"2500000.000"`), so it won't sum correctly until converted.

## Data model

`transfers` has two club columns (`from_club_id` and `to_club_id`), both pointing to the same `clubs` table. To handle that without extra DAX tricks, import `clubs` twice under two different names:

```
players (player_id) ---< transfers >--- buying_clubs (club_id = to_club_id)
                                    >--- selling_clubs (club_id = from_club_id)

buying_clubs (domestic_competition_id) ---< competitions (competition_id)
```

Steps:
1. Import `players`, `competitions`, and `clubs` twice (rename the copies `buying_clubs` and `selling_clubs`).
2. Relationships: `players[player_id] -> transfers[player_id]`, `buying_clubs[club_id] -> transfers[to_club_id]`, `selling_clubs[club_id] -> transfers[from_club_id]`, `buying_clubs[domestic_competition_id] -> competitions[competition_id]`.

## DAX measures

```dax
Total Transfers = COUNTROWS(transfers)

Money Spent = SUM(transfers[transfer_fee])

Money Received = SUM(transfers[transfer_fee])

Average Transfer Fee = AVERAGE(transfers[transfer_fee])

Max Transfer Fee = MAX(transfers[transfer_fee])
```

`Money Spent` and `Money Received` are the exact same formula - what changes is which table you use to slice them (`buying_clubs` vs `selling_clubs`). Same measure, different context, clearer labels.

## Pages

- **Overview**: total spending, total transfers, avg fee cards; spending trend by season.
- **Top Buyers**: bar chart of `buying_clubs[name]` by Money Spent.
- **Top Sellers**: bar chart of `selling_clubs[name]` by Money Received.
- **Players**: average fee by position, top 10 most expensive transfers table.
- **Competitions**: total spending by competition (via `buying_clubs`).

## Project Status

🔴 Not started - model and measures planned above, dashboard build pending
