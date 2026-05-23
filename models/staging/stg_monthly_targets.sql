with source as (
    select * from {{ ref('monthly_targets') }}
),

renamed as (
    select
        store_id,
        cast(year as int)           as target_year,
        cast(month as int)          as target_month,
        cast(sales_target as double) as sales_target,

        -- convenience: first day of the target month
        make_date(cast(year as int), cast(month as int), 1) as target_month_date
    from source
)

select * from renamed
