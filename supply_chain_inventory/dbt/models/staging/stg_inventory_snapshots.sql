-- Weekly stock position per product.
--
-- About 1% of readings arrive negative. A negative physical count is not a
-- state a warehouse can be in, so the reading is a measurement error - but
-- knowing it is wrong does not tell us what the true value was. Taking the
-- absolute value would invent a number that looks plausible and is not.
--
-- So the magnitude is discarded and the row is flagged instead. The same call
-- the wastewater project makes with missing sensor readings: the honest answer
-- is "we do not know", not a made-up one. Downstream, stock value simply
-- excludes these weeks rather than being quietly wrong.
--
-- Note on semantics: the source flags a stockout when demand exceeded stock,
-- before clamping the balance to zero. So a stockout week always ends at zero,
-- but a week can end at zero without a stockout if demand exactly matched
-- what was on hand. Only the first direction is an invariant worth testing.

with source as (

    select
        cast(product_id    as integer) as product_id,
        cast(snapshot_date as date)    as snapshot_date,
        cast(stock_on_hand as integer) as raw_stock_on_hand,
        cast(stockout      as integer) as is_stockout

    from {{ source('raw', 'inventory_snapshots') }}

)

select
    product_id,
    snapshot_date,
    case when raw_stock_on_hand >= 0 then raw_stock_on_hand end as stock_on_hand,
    raw_stock_on_hand < 0                                       as was_invalid_reading,
    is_stockout = 1                                             as is_stockout

from source
where snapshot_date is not null
