-- One row per purchase order.
--
-- Two defects are resolved here:
--   1. The generator duplicates ~1.5% of orders. Deduplicated on po_id,
--      keeping the first occurrence.
--   2. ~2% arrive with no supplier. The order itself is still valid
--      information - product, quantity and dates are intact - so the row is
--      kept and pointed at the unknown supplier member (-1) instead of being
--      dropped or left dangling.

with source as (

    select
        cast(po_id                  as integer) as po_id,
        cast(product_id             as integer) as product_id,
        try_cast(supplier_id        as integer) as supplier_id,
        cast(order_date             as date)    as order_date,
        cast(expected_delivery_date as date)    as expected_delivery_date,
        cast(actual_delivery_date   as date)    as actual_delivery_date,
        cast(quantity_ordered       as integer) as quantity_ordered

    from {{ source('raw', 'purchase_orders') }}

),

deduplicated as (

    select
        *,
        row_number() over (partition by po_id order by order_date) as occurrence

    from source

)

select
    po_id,
    product_id,
    coalesce(supplier_id, -1)                   as supplier_id,
    supplier_id is null                         as has_unknown_supplier,
    order_date,
    expected_delivery_date,
    actual_delivery_date,
    quantity_ordered,
    actual_delivery_date <= expected_delivery_date as is_on_time,
    date_diff('day', expected_delivery_date, actual_delivery_date) as days_late

from deduplicated
where occurrence = 1
