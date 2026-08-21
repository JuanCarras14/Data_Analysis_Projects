select
    supplier_id,
    supplier_name,
    region,
    nominal_lead_time_days,
    is_unknown_member

from {{ ref('stg_suppliers') }}
