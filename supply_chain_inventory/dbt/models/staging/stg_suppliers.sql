-- Supplier catalogue plus an explicit "unknown" member.
--
-- Some purchase orders arrive with no supplier on record. Rather than dropping
-- those orders or letting them join to nothing, they are pointed at supplier
-- -1. The gap stays visible in the totals instead of disappearing, and every
-- fact row keeps a valid foreign key.

with catalogue as (

    select
        cast(supplier_id            as integer) as supplier_id,
        cast(supplier_name          as varchar) as supplier_name,
        cast(region                 as varchar) as region,
        cast(nominal_lead_time_days as integer) as nominal_lead_time_days,
        false                                   as is_unknown_member

    from {{ source('raw', 'suppliers') }}

),

unknown_member as (

    select
        -1                          as supplier_id,
        'No supplier on record'     as supplier_name,
        'Unassigned'                as region,
        cast(null as integer)       as nominal_lead_time_days,
        true                        as is_unknown_member

)

select * from catalogue
union all
select * from unknown_member
