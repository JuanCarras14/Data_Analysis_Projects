# SQL Murder Mystery (first SQL project)

My first SQL project, before any of the others in this repo. A practice exercise based on the [SQL Murder Mystery by Knight Lab](https://mystery.knightlab.com/), where a murder case is solved by querying a relational database using SQL only. Keeping it here as a record of where I started with SQL.

## The case

> A crime has taken place and the detective needs help. The original crime scene report was lost, but it is known that a murder occurred on January 15, 2018 in SQL City.

The goal is to reconstruct the investigation from scratch using only SQL queries against a SQLite database containing information on people, interviews, driver's licenses, gym memberships, income, and event check ins.

## Tools used

- **DB Browser for SQLite**: initial exploration of the database
- **SQL (SQLite)**: all investigation queries

## Investigation process

1. **Crime report**: located the murder report from 01/15/2018 in SQL City, which pointed to two witnesses.
2. **Identifying witnesses**: cross referenced address data to find both witnesses (Morty Schapiro and Annabel Miller).
3. **Interviews**: both witnesses described the killer as a gold member of a gym ("Get Fit Now"), with a membership number starting in "48Z" and a license plate containing "H42W".
4. **Cross referencing suspects**: filtered the gym membership table by those conditions, returning two suspects.
5. **License plate verification**: joined with the driver's license table, narrowing it down to a single suspect matching both conditions.
6. **Check in verification**: confirmed with a correlated subquery that the suspect was at the gym on January 9, 2018, matching Annabel's testimony.
7. **Confession**: the suspect (Jeremy Bowers) confessed to being hired by a woman, providing a detailed physical description.
8. **Identifying the contractor**: by cross referencing gender, height, hair color, vehicle type, and attendance to a specific event (using `GROUP BY` and `HAVING`), the person behind the crime was identified.

## Result

**Jeremy Bowers** carried out the murder, hired by **Miranda Priestly**.

## Key takeaways

- Using `JOIN` across multiple tables to connect scattered information
- Correlated subqueries to compare check in and check out times
- `GROUP BY` and `HAVING` to filter by event frequency
- Structured investigation, where each query builds on the clue found in the previous one

## Files

- `database/`: SQLite database for the exercise
- `queries/investigation.sql`: the 9 queries from the investigation process, commented step by step