-- Weekly stock fact, one row per product per week, carrying the value of the
-- stock and the length of the stockout run it belongs to.
--
-- The consecutive-week count uses the classic gaps-and-islands trick: for rows
-- ordered by date, (row_number over all rows) minus (row_number over stockout
-- rows only) stays constant while a stockout run continues and shifts when it
-- breaks, which turns the run into a group we can count.

with snapshots as (

    select
        s.product_id,
        s.snapshot_date,
        s.stock_on_hand,
        s.was_invalid_reading,
        s.is_stockout,
        p.category,
        p.unit_cost,
        p.reorder_point,
        s.stock_on_hand * p.unit_cost as stock_value

    from {{ ref('stg_inventory_snapshots') }} as s
    inner join {{ ref('stg_products') }} as p
        on s.product_id = p.product_id

),

runs as (

    select
        *,
        row_number() over (partition by product_id order by snapshot_date)
            - row_number() over (partition by product_id, is_stockout order by snapshot_date)
            as run_group

    from snapshots

)

select
    product_id,
    category,
    snapshot_date,
    stock_on_hand,
    unit_cost,
    stock_value,
    reorder_point,
    stock_on_hand <= reorder_point as is_below_reorder_point,
    was_invalid_reading,
    is_stockout,
    case
        when is_stockout
        then count(*) over (partition by product_id, is_stockout, run_group)
    end as stockout_run_weeks

from runs
