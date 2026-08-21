select
    product_id,
    product_name,
    category,
    unit_cost,
    reorder_point,
    order_quantity

from {{ ref('stg_products') }}
