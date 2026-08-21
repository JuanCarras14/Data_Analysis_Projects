-- The unknown-supplier orders must survive the pipeline.
--
-- It would be easy to "fix" the missing-supplier problem by dropping those
-- rows, which would make every test pass and quietly understate order volume.
-- This test fails if that ever happens: the count of orders flagged as having
-- an unknown supplier must match the count of raw orders with a blank supplier
-- once duplicates are removed.

with expected as (

    select count(distinct po_id) as n
    from {{ source('raw', 'purchase_orders') }}
    where supplier_id is null or trim(cast(supplier_id as varchar)) = ''

),

actual as (

    select count(*) as n
    from {{ ref('fct_purchase_orders') }}
    where has_unknown_supplier

)

select
    expected.n as expected_orders,
    actual.n   as actual_orders

from expected
cross join actual
where expected.n != actual.n
