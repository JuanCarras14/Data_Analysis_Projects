-- One row per supplier: the reliability picture the dashboard reads.
--
-- The unknown member is excluded from the ranking on purpose. Its orders are
-- real and stay in the order totals, but a supplier that was never recorded
-- cannot be scored for on-time delivery, and leaving it in would put a
-- meaningless row at the top or bottom of the league table.

with orders as (

    select *
    from {{ ref('fct_purchase_orders') }}
    where not has_unknown_supplier

)

select
    supplier_id,
    supplier_name,
    region,
    nominal_lead_time_days,
    count(*)                                                as total_orders,
    count(*) filter (where is_on_time)                      as on_time_orders,
    count(*) filter (where not is_on_time)                  as late_orders,
    round(avg(case when is_on_time then 1.0 else 0.0 end), 4) as on_time_rate,
    round(avg(actual_lead_time_days), 1)                    as avg_actual_lead_time_days,
    round(avg(actual_lead_time_days) - avg(nominal_lead_time_days), 1) as lead_time_gap_days,
    rank() over (order by avg(case when is_on_time then 1.0 else 0.0 end) desc) as reliability_rank

from orders
group by 1, 2, 3, 4
