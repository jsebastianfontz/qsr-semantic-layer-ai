with stores as (
    select * from {{ ref('stg_stores') }}
),

enriched as (
    select
        store_id,
        store_name,
        city,
        state,
        region,
        open_date,

        -- months since open as of the last date in the dataset
        datediff('month', open_date, date '2024-12-31') as months_since_open,

        -- flag: open for 12+ months before the analysis window starts (2023-01-01)
        case
            when open_date <= date '2022-01-01' then true
            else false
        end as is_same_store_eligible,

        -- cohort year
        year(open_date) as open_year
    from stores
)

select * from enriched
