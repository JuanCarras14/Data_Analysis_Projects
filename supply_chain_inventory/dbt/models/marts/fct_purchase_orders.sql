-- Purchase order fact, one row per order, joined to the supplier that placed
-- it. Orders with no supplier on record resolve to the unknown member, so they
-- stay in the totals and can be counted rather than quietly lost.

select
    po.po_id,
    po.product_id,
    po.supplier_id,
    s.supplier_name,
    s.region,
    po.has_unknown_supplier,
    po.order_date,
    po.expected_delivery_date,
    po.actual_delivery_date,
    po.quantity_ordered,
    po.is_on_time,
    po.days_late,
    s.nominal_lead_time_days,
    date_diff('day', po.order_date, po.actual_delivery_date) as actual_lead_time_days

from {{ ref('stg_purchase_orders') }} as po
inner join {{ ref('stg_suppliers') }} as s
    on po.supplier_id = s.supplier_id
