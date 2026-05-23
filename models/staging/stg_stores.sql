with source as (
    select * from {{ ref('stores') }}
),

renamed as (
    select
        store_id,
        store_name,
        city,
        state,
        region,
        cast(open_date as date) as open_date
    from source
)

select * from renamed
