with source as (
    select * from {{ ref('daily_sales') }}
),

renamed as (
    select
        store_id,
        cast(sale_date as date)     as sale_date,
        cast(gross_sales as double)    as gross_sales,
        cast(net_sales as double)      as net_sales,
        cast(digital_sales as double)  as digital_sales,
        cast(in_store_sales as double) as in_store_sales,
        cast(transaction_count as int) as transaction_count,

        -- derived
        net_sales - digital_sales - in_store_sales as channel_rounding_diff
    from source
)

select * from renamed
