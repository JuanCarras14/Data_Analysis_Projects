-- Product catalogue, typed and renamed. No cleaning needed here: the
-- generator does not inject defects into products.

select
    cast(product_id     as integer)  as product_id,
    cast(product_name   as varchar)  as product_name,
    cast(category       as varchar)  as category,
    cast(supplier_id    as integer)  as catalogue_supplier_id,
    cast(unit_cost      as decimal(10, 2)) as unit_cost,
    cast(reorder_point  as integer)  as reorder_point,
    cast(order_quantity as integer)  as order_quantity

from {{ source('raw', 'products') }}
